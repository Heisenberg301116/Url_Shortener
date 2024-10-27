from config.database import collection_name
from models.models import UrlMappingModel
from config.cache import cached_obj as cache
from celery import Celery
from utils.utils import create_short_code, DNS as dns
import re

# Configure the Celery application
celery_app = Celery(
    'my_fastapi_app',
    broker='redis://localhost:6379/0',  # receive tasks
    backend='redis://localhost:6379/0'      # storing result
)


db = UrlMappingModel(collection_name, cache)



@celery_app.task
def process_short_code(short_code: str):    
    long_url = db.get_long_url(short_code)
           
    if long_url:
        return {"type": "long_url", "long_url": long_url}
    else:
        return {"type": "long_url", "long_url": ""}
    
    
@celery_app.task
def process_long_url(long_url : str, custom_slug : str, expire_duration: int):
    short_code = db.get_short_code(long_url)
    
    if not short_code:       
        short_code = custom_slug if custom_slug else create_short_code()      
        # if the short URL already in DB, keep creating new ones
        while db.get_long_url(short_code):
            short_code = custom_slug + create_short_code()                   
        db.insert_url_mapping(short_code, long_url, expire_duration)
        short_url = f"{dns}/{short_code}"    
        return {"type": "short_url", "created_new": True, "short_url": short_url}
    
    else:        
        short_url = f"{dns}/{short_code}"    
        return {"type": "short_url", "created_new": False, "short_url": short_url}


@celery_app.task
def process_delete_url(short_code, long_url):
    res = db.delete_from_cache_and_collection(short_code=short_code, long_url=long_url)
        
    return {"type": "delete_url", "message": res}