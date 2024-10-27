from datetime import datetime, timedelta, timezone
import json

class UrlMappingModel:
    def __init__(self, collection_name, memcache_client):
        self.collection = collection_name
        self.memcache = memcache_client


    def delete_from_cache_and_collection(self, short_code: str = "", long_url: str = "",) -> str :        
        if long_url == "":
            doc_to_delete = self.collection.find_one({"short_code": short_code})
        else:
            doc_to_delete = self.collection.find_one({"long_url": long_url})
                    
        if doc_to_delete:            
            long_url_value = doc_to_delete.get('long_url')
            short_code_value = doc_to_delete.get('short_code')
            self.memcache.delete(long_url_value)                
            self.memcache.delete(short_code_value)            
            result = self.collection.delete_one({"short_code": short_code_value})
            if result.deleted_count > 0:
                return "Success"
            else:
                return "Failed"
        else:
            return "Not Found"
            
     
            
    def handle_expiry(self, short_code: str, expiry_time) -> bool:
        # Ensure expiry_time is a timezone-aware datetime
        if isinstance(expiry_time, datetime) and expiry_time.tzinfo is None:
            # If expiry_time is naive, set it to UTC
            expiry_time = expiry_time.replace(tzinfo=timezone.utc)
        
        if expiry_time and expiry_time > datetime.now(timezone.utc):
            return True
        else:
            self.delete_from_cache_and_collection(short_code=short_code)
            return False
            
            
        
    def get_short_code(self, long_url: str) -> str:
        # Check cache first
        cached_data = self.memcache.get(long_url)
        if cached_data:
            # Decode bytes to string and then load the JSON string into a dictionary
            cached_data = json.loads(cached_data.decode('utf-8'))
            
            short_code = cached_data.get('short_code')
            expiry_time = datetime.fromisoformat(cached_data.get('expiry_time'))
        else:
            mapping = self.collection.find_one({"long_url": long_url})
            if mapping:
                short_code = mapping['short_code']
                expiry_time = mapping['expiry_time']                
                self.memcache.set(long_url, json.dumps({"short_code": short_code, "expiry_time": expiry_time.isoformat()}), expire=3600)
            else:
                return None
            
        res = self.handle_expiry(short_code, expiry_time)
        if res == True:
            return short_code
        else:
            return None
        


    def get_long_url(self, short_code: str) -> str:
        # Check cache first
        cached_data = self.memcache.get(short_code)        
        
        if cached_data:
            # Decode bytes to string and then load the JSON string into a dictionary
            cached_data = json.loads(cached_data.decode('utf-8'))            
            long_url = cached_data.get("long_url")
            expiry_time = datetime.fromisoformat(cached_data.get("expiry_time"))        
        else:
            mapping = self.collection.find_one({"short_code": short_code})
            if mapping:
                long_url = mapping['long_url']
                expiry_time = mapping['expiry_time']
                self.memcache.set(short_code, json.dumps({"long_url": long_url, "expiry_time": expiry_time.isoformat()}), expire=3600)                           
            else:
                return None
            
        res = self.handle_expiry(short_code, expiry_time)
        if res == True:
            return long_url
        else:
            return None
        
                          
                         

    def insert_url_mapping(self, short_code: str, long_url: str, expiry_duration: int = -1) -> None:
        # Calculating expiry time as current time + expiry_duration in seconds
        if expiry_duration is not -1:
            expiry_time = datetime.now(timezone.utc) + timedelta(seconds=expiry_duration)
        else:   # Set expiry_time to a very distant future date
            expiry_time = datetime.max.replace(tzinfo=timezone.utc)
    
        # Insert data into the database
        self.collection.insert_one({"short_code": short_code, "long_url": long_url, "expiry_time" : expiry_time})
        
        # Update cache
        self.memcache.set(long_url, json.dumps({"short_code": short_code, "expiry_time": expiry_time.isoformat()}), expire=3600)       
        
        self.memcache.set(short_code, json.dumps({"long_url": long_url, "expiry_time": expiry_time.isoformat()}), expire=3600)