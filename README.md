## Table of Contents
1. [Project Overview](#1-project-overview)
   - [Introduction](#11-introduction)
   - [Approach for generating unique Short URL](#12-approach-for-generating-unique-short-url)
   - [Functional Requirements](#13-functional-requirements)
   - [Core Requirements](#14-core-requirements)
   - [Additional Functionalities](#15-additional-functionalities)
   - [API Specifications](#16-api-specifications)
     
2. [Setting Up the Project on Windows Local System](#2-setting-up-the-project-on-windows-local-system)
   - [Setting up the MongoDB Atlas Database](#21-setting-up-the-mongodb-atlas-database)
   - [Setting up the Virtual Environment](#22-setting-up-the-virtual-environment)
     
3. [Running the Project on Windows Local System](#3-running-the-project-on-windows-local-system)
   - [Setting up Docker Services](#31-setting-up-docker-services)
   - [Starting the Celery Worker](#32-starting-the-celery-worker)
   - [Running the Main FastAPI Application](#33-running-the-main-fastapi-application)

---
---

## 1) Project Overview

### 1.1) Introduction
This is a FastAPI application built in Python to generate random short URLs for given long URLs. Designed to handle concurrent operations of multiple workers with high availability by enqueuing jobs into Redis cache.

---

### 1.2) Approach for generating unique Short URL:
The code for generating random Short Code is present at 'utils/utils.py'. Here, we are generating the code of length at-least 1 and at-max 5. For generating each character, we can use the set containing characters from 0-9, a-z and A-Z. Thus, we have 62 choices to fill each character. Thus, 
- For a code of length 1, there are 62 permutations.
- For a code of length 2, there are 62*62 permutations.
- For a code of length 5, there are 62^5 permutations.

Thus, our logic is capable of supporting around 930 million URLs. Note that the random generator is prone to collision, meaning it can produce the short code that has already been in use for some other Long URL. Thus, we will keep on generating the Short code until we find that such short code that has not been in use till now.

---

### 1.3) Functional Requirements
To build a backend application powered by FastAPI supporting the following operations:
1. **URL Shortening**: Given a long URL, return a much shorter URL.
2. **URL Redirecting**: Given a shorter URL, redirect to the original URL.

---

### 1.4) Core Requirements
#### a) Data Persistence Across Instances
Data persistence across instances is ensured using MongoDB Atlas as the primary database, storing original URLs and their shortened counterparts, allowing consistent data access across application instances. 
#### b) Concurrency and Multiple Workers
Multiple workers are set up using the `uvicorn` command, where the number of workers can be specified (e.g., `uvicorn main:app --reload --workers <number>`). Concurrency is achieved through a task queue with Celery, which distributes tasks across worker processes. Redis acts as the message broker, enabling quick communication between the web application and workers to ensure prompt task execution.
#### c) Performance and Scalability
Performance is achieved through asynchronous programming with FastAPI, enabling the application to handle multiple requests concurrently. To reduce database load, Memcache stores recent user requests and responses.
For scalability, the application can run on multiple workers, easily adjustable via the `uvicorn` command. MongoDB Atlas is used for database scaling and optimization, allowing the application to manage increasing data and user load effectively.
#### d) High Availability
High availability is ensured as FastAPI instances enqueue jobs into Celery without waiting for completion, allowing each instance to accept new requests without delay. A unique job ID is returned to the client to track progress, ensuring high responsiveness and the ability to handle high request volumes efficiently.

---

### 1.5) Additional Functionalities
#### a) Custom Short URLs
Users can specify a custom URL slug for their shortened link. If available, the application maps it to the user’s long URL. If taken, unique characters are appended to ensure a unique URL mapping.
#### b) Expiration
An expiration mechanism allows users to set a time duration (in seconds) after which the short URL will no longer be valid. By default, short URLs are set to exist indefinitely, allowing flexible temporary or permanent link options.
#### c) Rate Limiting
To prevent abuse, URL shortening requests are limited to a maximum of 10 requests per user or IP address within a 1-minute period, ensuring fair resource use and consistent service quality.

---

### 1.6) API Specifications
**a) POST /url/shorten:** This endpoint enqueues the job of generating a shortened URL into Redis for Celery to process. It accepts 3 parameters in its body: 
   1) **long_url**: The URL that you want to shorten (Required parameter).
   2) **custom_slug**: Any custom name you want to give to your Short URL (Optional parameter).
   3) **expire_duration**: Duration in seconds after which the Short URL generated would expire (Optional parameter and by default set to infinite time period).

Note that the DNS: `http://magic.Link/` will be added to the random short code generated for a given Long URL. Thus, if the Short Code is like this: "ha34", the Short URL would be: `http://magic.Link/ha34`.

The above endpoint will return the task_id. Based of it we can check the status of the given job/task from time to time until it gets completed.

**b) GET /{short_code}:** This endpoint enqueues the job of fetching the long_url from the given Short Code. Notice that it accepts the short code as a parameter and not the short url. Thus, if your Short URL is like this: `http://magic.Link/g2hd4` then the short code for this would be "g2hd4". Thus you will specify this short code and not the full short url. 

This endpoint will also return the task_id for checking status of the job.

**c) DELETE /:** This endpoint enqueues the job of deleting the mapping of Long URL to the Short URL both from the MongoDB database as well as from the Memcache. It accepts the following 2 parameters in its body and you need to specify any one to delete that specific mapping.
   1) **short_code**: The short code for the given Long URL whose mapping you want to delete.
   2) **long_url**: The given Long URL whose mapping you want to delete.

Again, this endpoint returns task_id.

**d) GET /{task_id}:** This endpoint is used to track the status of the given task_id. Based upon the nature of the job corresponding to this task_id, it returns one out of the following responses:
   1) **Pending (200 OK):** It signifies that the given job is still waiting in the Redis queue to get processed.
   2) **Failure (500 Internal Server Error):** It signifies that the job encountered an error during execution.
   3) **Completed (404 Not Found):** It tells that the job of fetching Long URL from Short Code was completed and no such Short Code was present in the database.
   4) **Completed (302 Temporary Redirect):** It conveys completion of the job of fetching Long URL from Short Code and successfully finds the Long URL corresponding to the given Short Code and redirects to this Long URL.
   5) **Completed (201 Resource Created):** It conveys completion of the job of creating a Short URL from the given Long URL and returns that new Short URL in its response.
   6) **Completed (200 OK):** It conveys completion of the job of creating a Short URL from the given Long URL. But the given Long URL was already present in the record, so instead of creating a new Short URL, it returned that existing Short URL.
   7) **Completed (204 No Content):** It conveys completion of the job of deleting a specific Long URL to Short Code mapping both in the Memcache and MongoDB database. The record was deleted successfully.
   8) **Completed (400 Bad Request):** It conveys completion of the job of deleting a specific Long URL to Short Code mapping both in the Memcache and MongoDB database. The job failed while executing and deletion was unsuccessful. 
   9) **Completed (404 Not Found):** It conveys completion of the job of deleting a specific Long URL to Short Code mapping both in the Memcache and MongoDB database. No such record to be deleted was found in the database.
      
---
---


## 2) Setting Up the Project on Windows Local System

### 2.1) Setting up the MongoDB Atlas Database
1. Clone this repository to your local system.
2. Create a cluster in MongoDB Atlas and note the username, password, and connection string.
3. Create a `.env` file in the root directory of this cloned project, with the following:
      - MONGODB_USERNAME=`Your username`
      - MONGODB_PASSWORD=`Your password`
5. Set the `uri` variable in './config/database.py' to the connection string of your cluster.

---

### 2.2) Setting up the Virtual Environment
1. Open CMD and navigate to the project directory.
2. Create a virtual environment by running: `python -m venv myvenv`
3. Activate the virtual environment with: `myvenv\Scripts\activate`
4. Install the required packages with: `pip install -r requirements.txt`
5. Close CMD.

---
---

## 3) Running the Project on Windows Local System

### 3.1) Setting up Docker Services 
1. Open Docker Desktop App to start Docker services.
2. Open CMD.
3. Start Memcache with: `docker run -d --name memcached -p 11211:11211 memcached:latest`
4. Start Redis with: `docker run -d --name redis -p 6379:6379 redis:latest`
5. If issues arise, start services directly via Docker Desktop App GUI.

---

### 3.2) Starting the Celery Worker
1. Open CMD in the root directory and run: `celery -A worker.celery_worker.celery_app worker --loglevel=info --pool=solo`

---

### 3.3) Running the Main FastAPI Application
1. Open CMD in the root directory.
2. Activate the virtual environment with: `myvenv\Scripts\activate`
3. Start the application with: `uvicorn main --reload --workers 4`
