import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import Database
from  models.models import Login, Response, PostVehicle, PostDriver, PostDrive, PostManager
from logger.logger import Logger
import yaml

import json

restlin = None
app = None

class Restlin:
    def __init__(self):
        self.__CONFIG = "../config/config.config"
        self.__APP = FastAPI()
        self.__HOST = ''
        self.__PORT = ''
        self.__LOGIN = Login(username='', password='')
        self.__APP.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"]
        )
        self.__get_config()
        self.__LOGGER = Logger('restlin')

    def __get_config(self):
        with open(self.__CONFIG, 'r') as stream:
            restlin = yaml.load(stream, Loader=yaml.FullLoader)['RESTLIN']
            self.__HOST = restlin['HOST']
            self.__PORT = restlin['PORT']

    def set_login(self, login: Login):
        self.__LOGIN.username = login.username
        self.__LOGIN.password = login.password

    def get_login(self):
        return self.__LOGIN
    
    def start_unicorn(self):
        uvicorn.run(self.__APP, host=self.__HOST, port=self.__PORT, log_level='error')

    def get_app(self):
        return self.__APP

    def log_info(self, msg):
        self.__LOGGER.log_info(msg)

    def log_warning(self, msg):
        self.__LOGGER.log_warning(msg)

    def log_error(self, msg):
        self.__LOGGER.log_error(msg)


if __name__ == "__main__":
    restlin = Restlin()
    app = restlin.get_app()

# POST ROUTE FOR CREATING A USER
@app.post("/user")
def log_in(login: Login):
    restlin.set_login(login)
    response = Response()

    try:
        db = Database(login.username, login.password)
        if(db.is_admin()):
            response.admin = True
        else:
            response.admin = False
            group = db.get_group()
            response.branch_id = group
    except Exception as e:
        restlin.log_error(f"Exception raised in post route /user: {e}")
        response.error = True
    restlin.log_info(f"User login: {login.username}")
    return response

@app.get("/managers")
def get_managers(branch_id: int):
    login = restlin.get_login()
    db = Database(login.username, login.password)
    managers = db.get_managers(branch_id=branch_id)
    return managers

@app.get("/drivers/")
def get_drivers(branch_id: int):
    login = restlin.get_login()
    db = Database(login.username, login.password)
    drivers = db.get_drivers(branch=branch_id)
    return drivers

@app.get("/vehicles/")
def get_vehicles(branch_id: int):
    login = restlin.get_login()
    db = Database(login.username, login.password)
    vehicles = db.get_vehicles(branch=branch_id)
    return vehicles

@app.get("/drives/")
def get_drives(branch_id: int):
    login = restlin.get_login()
    db = Database(login.username, login.password)
    drives = db.get_drives(branch=branch_id)
    return drives

@app.post("/add/manager")
def add_manager(manager: PostManager, branch_id: int):
    login = restlin.get_login()
    db = Database(login.username, login.password)
    response = db.add_manager(manager=manager, branch_id=branch_id)
    return {"status": "ok" if response else "error"}

@app.post("/add/driver")
def add_driver(driver: PostDriver, branch_id: int):
    login = restlin.get_login()
    db = Database(login.username, login.password)
    response = db.add_driver(driver=driver, branch_id=branch_id)
    return {"status": "ok" if response else "error"}

@app.post("/add/vehicle")
def add_vehicle(vehicle: PostVehicle, branch_id: int):
    login = restlin.get_login()
    db = Database(login.username, login.password)
    response = db.add_vehicle(vehicle=vehicle, branch_id=branch_id)
    return {"status": "ok" if response else "error"}

@app.post("/add/drive")
def add_drive(drive: PostDrive, branch_id: int):
    login = restlin.get_login()
    db = Database(login.username, login.password)
    response = db.add_drive(drive=drive, branch_id=branch_id)
    return {"status": "ok" if response else "error"}

@app.delete("/delete/driver")
def delete_driver(branch_id, driver_id):
    login = restlin.get_login()
    db = Database(login.username, login.password)
    response = db.delete_driver(driver_id=driver_id, branch_id=branch_id)
    return {"status": "ok" if response else "error"}

@app.delete("/delete/vehicle")
def delete_vehicle(branch_id, vehicles_id):
    login = restlin.get_login()
    db = Database(login.username, login.password)
    response = db.delete_vehicle(vehicles_id=vehicles_id, branch_id=branch_id)
    return {"status": "ok" if response else "error"}


@app.delete("/delete/drive")
def delete_drive(branch_id, drive_id):
    login = restlin.get_login()
    db = Database(login.username, login.password)
    response = db.delete_drive(drive_id=drive_id, branch_id=branch_id)
    return {"status": "ok" if response else "error"}

@app.put("/activate/drive")
def activate_drive(branch_id, drive_id):
    login = restlin.get_login()
    db = Database(login.username, login.password)
    response = db.set_drive_active(drive_id=drive_id, branch_id=branch_id)
    return {"status": "ok" if response else "error"}

@app.put("/finish/drive")
def finish_drive(branch_id, drive_id):
    login = restlin.get_login()
    db = Database(login.username, login.password)
    response = db.set_drive_finished(drive_id=drive_id, branch_id=branch_id)
    return {"status": "ok" if response else "error"}

if __name__ == "__main__":
    restlin.start_unicorn()
