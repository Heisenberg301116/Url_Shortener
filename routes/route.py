from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from celery.result import AsyncResult
from schema.schema import UrlMappingSchema
from schema.schema import DeleteUrlRequest
# from schema.schema import GetLongUrlSchema
from fastapi.responses import RedirectResponse
from fastapi.responses import JSONResponse
from rate_limit.redis_rate_limit import is_rate_limited
from worker.celery_worker import process_short_code, process_long_url, process_delete_url


router = APIRouter()


@router.post("/longurl")
async def shorten_url(request: Request, url_mapping: UrlMappingSchema):
    user_id = request.client.host  # IP address of user
    
    if is_rate_limited(user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
    
    long_url = str(url_mapping.long_url)
    custom_slug = url_mapping.custom_slug
    expire_duration = url_mapping.expire_duration       
    
    # Enqueue the task to process the long URL
    task = process_long_url.delay(long_url, custom_slug, expire_duration)   
    return {"task_id": task.id, "status": "Task is processing !"}
    
    
    
@router.get("/{short_code}")
async def get_long_url(short_code: str, request: Request):
    user_id = request.client.host  # IP address of user
    
    print("===============> shorturl = ",short_code)
    if is_rate_limited(user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
    
    # Enqueue the task to process the short code
    task = process_short_code.delay(short_code)
    return {"task_id": task.id, "status": "Task is processing !"}



@router.delete("/delete")
async def delete_url(request: Request, url_request: DeleteUrlRequest):
    user_id = request.client.host  # IP address of user
    
    if is_rate_limited(user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
    
    short_code = url_request.short_code
    long_url = url_request.long_url    
    
    if short_code is None and long_url is None:
        raise HTTPException(status_code=400, detail="At least one of short_code or long_url must be provided.")
    else:        
        task = process_delete_url.delay(short_code, long_url)        
        return {"task_id": task.id, "status": "Task is processing !"}



@router.get("/task/{task_id}")
async def get_task_result(task_id: str):
    result = AsyncResult(task_id)
    
    if result.state == "PENDING":
        return {"task_id": task_id, "status": "Pending..."}
    elif result.state == "FAILURE":
        return {"task_id": task_id, "status": "Failed", "result": str(result.result)}
    else:
        response = result.result  # Now this is a dict               
        
        if response['type'] == "long_url":
            if response['long_url'] == "":
                return JSONResponse(content={"task_id": task_id, "status": "Completed", "result": "URL not found !"}, status_code=404)
                
            else:
                return RedirectResponse(url=response['long_url'], status_code=307)
        
        
        
        elif response['type'] == "short_url":
            if response["created_new"] == True:
                return JSONResponse(content={"task_id": task_id, "status": "Completed", "result": response['short_url']}, status_code=201)
            else:
                return JSONResponse(content={"task_id": task_id, "status": "Completed", "result": response['short_url']}, status_code=200)
        
        
        
        elif response['type'] == "delete_url":
            if response['message'] == "Success":
                return JSONResponse(content={"task_id": task_id, "status": "Completed", "result": "Successfully deleted !"}, status_code=204)               
            
            elif response['message'] == "Failed":
                return JSONResponse(content={"task_id": task_id, "status": "Completed", "result": "Failed to delete !"},status_code=400)
    
            elif response['message'] == "Not Found":
                return JSONResponse(content={"task_id": task_id, "status": "Completed", "result": "URL not found !"}, status_code=404)            