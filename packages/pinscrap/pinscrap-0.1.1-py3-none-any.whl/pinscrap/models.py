from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List

class PinCreator(BaseModel):
    username: str
    profile_url: Optional[HttpUrl] = None

class Pin(BaseModel):
    id: str
    image_url: HttpUrl = Field(alias="imageURL")
    description: Optional[str] = ""
    link: Optional[HttpUrl] = None
    creator: Optional[PinCreator] = None

class SearchResult(BaseModel):
    query: str
    pin_count: int
    pins: List[Pin]
    