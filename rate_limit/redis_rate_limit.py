from redis import Redis
import time

# Rate limit settings
RATE_LIMIT = 10  # max requests
RATE_LIMIT_PERIOD = 60  # per minute
EXPIRY_TIME = 3600  # expiry time for user data in redis


# Connect to Redis
redis_client = Redis(host='localhost', port=6379, db=0)


def is_rate_limited(user_id: str) -> bool:    
    current_time = int(time.time())
    user_info = redis_client.hgetall(user_id)
    
    if not user_info:
        # print("=====================> user id = ",user_id," and count = ",0)
        redis_client.hset(user_id, mapping={
            "count": 1,
            "first_request_time": current_time
        })
        redis_client.expire(user_id, EXPIRY_TIME)
        return False
        
    else:
        # Decode the values from bytes
        count = int(user_info.get(b'count', 0))
        first_request_time = int(user_info.get(b'first_request_time', 0))
        
        if count < RATE_LIMIT:
            # print("=====================> user id = ",user_id," and count = count+1")
            redis_client.hincrby(user_id, "count", 1)
            return False
        
        elif current_time - first_request_time > RATE_LIMIT_PERIOD:
            # print("=====================> user id = ",user_id," and count = resetting to 1")
            redis_client.hset(user_id, mapping={
                "count": 1,
                "first_request_time": current_time
            })
            redis_client.expire(user_id, EXPIRY_TIME)
            return False
        
        else:
            return True