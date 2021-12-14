from typing import List, Optional
from pydantic import BaseModel

class Login(BaseModel):
    username: str
    password: str
    group: Optional[str]

class Data(BaseModel):
    name: Optional[str]
    phone: Optional[str]
    adress: Optional[str]
    salary: Optional[float]
    statuses: Optional[List[int]]

class Response(BaseModel):
    error: bool = False
    admin: bool = False
    branch_id: Optional[str]
    data: Optional[List[Data]]

class Managers(BaseModel):
    name: Optional[str]
    oid: Optional[str]

class Drivers(BaseModel):
    id: Optional[int]
    fio: Optional[str]
    driving_licence: Optional[str]
    earnings: Optional[float]
    status: Optional[str]

class Vehicles(BaseModel):
    id: Optional[int]
    mark: Optional[str]
    carry_capacity: Optional[float]
    status: Optional[str]
    driver_id: Optional[int]

class Drives(BaseModel):
    id: Optional[int]
    driver_id: Optional[int]
    vehicles_id: Optional[int]
    cargo_weight: Optional[float]
    destination: Optional[str]
    destination_distance: Optional[int]
    price: Optional[float]

class PostVehicle(BaseModel):
    carry_capacity: Optional[float]
    mark: Optional[str]
    driver_id: Optional[int]

class PostDriver(BaseModel):
    fio: Optional[str]
    driving_licence: Optional[str]

class PostDrive(BaseModel):
    driver_id: Optional[int]
    vehicles_id: Optional[int]
    cargo_weight: Optional[float]
    destination: Optional[str]
    destination_distance: Optional[int]
    price: Optional[float]

class PostManager(BaseModel):
    name: str
    password: str
