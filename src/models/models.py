from typing import List
from pydantic import BaseModel

class Login(BaseModel):
    username: str
    password: str

class Data(BaseModel):
    name: str = None
    phone: str = None
    adress: str = None
    salary: float = None
    statuses: List[int] = None

class Response(BaseModel):
    error = False
    admin = False
    services: List[str] = None
    data: List[Data] = None
