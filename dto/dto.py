from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date

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