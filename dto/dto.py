from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date

### file    
class FileUploadedItem(BaseModel):
    file_name: str
    file_content: bytes
    
class FileUploadRequest(BaseModel):
    files: List[FileUploadedItem]

class FileDeleteRequest(BaseModel):
    file_ids: List[int]

class FileItem(BaseModel):
    id: int
    file_key: str
    file_url: str
    created_at: datetime
    
class GetFileListResponse(BaseModel):
    data: List[FileItem]

class CreateConcert(BaseModel):
    name: str
    description: str
    seat_count: int
    date: date
    place: str
    price: int
    image: str

class Test(BaseModel):
    files: List[bytes]