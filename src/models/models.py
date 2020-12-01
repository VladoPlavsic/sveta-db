from typing import List, Optional
from pydantic import BaseModel

class Login(BaseModel):
    username: str
    password: Optional[str]

class Data(BaseModel):
    name: Optional[str]
    phone: Optional[str]
    adress: Optional[str]
    salary: Optional[float]
    statuses: Optional[List[int]]

class Response(BaseModel):
    error: bool = False
    admin: bool = False
    services: Optional[List[str]]
    data: Optional[List[Data]]

class Updates(BaseModel):
    update: Optional[bool] = False
    service: Optional[str]
    status: Optional[str]

class ClientUpdates(BaseModel):
    clientname: Optional[str]
    clientnumber: Optional[str]
    updated: List[Updates]

class Managers(BaseModel):
    username: Optional[str]

class Clients(BaseModel):
    id_: Optional[int]
    fio: Optional[str]
    tel: Optional[str]
    job: Optional[str]
    homeadress: Optional[str]
    salary: Optional[str]
    call_back: bool = False

class Services(BaseModel):
    id_: Optional[int]
    service: Optional[str]
    service_description: Optional[str]

class ID(BaseModel):
    id_: Optional[int]
