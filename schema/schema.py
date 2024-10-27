from typing import Optional
from pydantic import BaseModel, Field, HttpUrl

class UrlMappingSchema(BaseModel):
    long_url: HttpUrl
    custom_slug: Optional[str] = Field(default="")
    expire_duration: Optional[int] = Field(default=-1)
    
    
class DeleteUrlRequest(BaseModel):
    short_code: Optional[str] = Field(default="")
    long_url: Optional[str] = Field(default="")