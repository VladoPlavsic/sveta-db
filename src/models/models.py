from typing import List
from pydantic import BaseModel

class Login(BaseModel):
    username: str = None
    password: str = None

class Data(BaseModel):
    name: str = None
    phone: str = None
    adress: str = None
    salary: float = None
    statuses: List[int] = None

class Response(BaseModel):
    error: bool = False
    admin: bool = False
    services: List[str] = None
    data: List[Data] = None

class Updates(BaseModel):
    update: bool = False
    service: str = None
    status: str = None

class ClientUpdates(BaseModel):
    clientname: str = None
    clientnumber: str = None
    updated: List[Updates] = None
    username: str = None
    password: str = None

class Managers(BaseModel):
    username: str = None

class Clients(BaseModel):
    id_: int = None
    fio: str = None
    tel: str = None
    job: str = None
    homeadress: str = None
    salary: str = None
    call_back: bool = True

class Services(BaseModel):
    id_: int = None
    service: str = None
    service_description: str = None

class ID(BaseModel):
    id_: int = None
