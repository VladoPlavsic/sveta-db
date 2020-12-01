import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import Database
from  models.models import Login, Response, Data, ClientUpdates, Managers, Clients, Services, ID
from logger.logger import Logger
import yaml

restlin = None
app = None

class Restlin:
    def __init__(self):
        self.__CONFIG = "../config/config.config"
        self.__APP = FastAPI()
        self.__HOST = ''
        self.__PORT = ''
        self.__LOGIN = Login()
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
        response = db.get_data_for_managers()
        if(db.is_admin()):
            response.admin = True
        else:
            response.admin = False
    except Exception as e:
        restlin.log_error(f"Exception raised in post route /user: {e}")
        response.error = True
    restlin.log_info(f"User login: {login.username}")
    return response

@app.put("/update")
def update_user(client_updates: ClientUpdates):
    login = restlin.get_login()
    db = Database(login.username, login.password)
    for s in client_updates.updated:
        if s.update and s.status:
                db.update_client_live(clientname=client_updates.clientname, clientnumber=client_updates.clientnumber,servicename=s.service,statusname=s.status)
    restlin.log_info(f"Client {client_updates.clientname} status updated by: {login.username}")
    return True

@app.get("/managers")
def get_managers():
    login = restlin.get_login()
    db = Database(login.username, login.password)
    response = db.get_managers()
    return response

@app.get("/clients")
def get_clients():
    login = restlin.get_login()
    db = Database(login.username, login.password)
    response = db.get_clients()
    return response

@app.get("/services")
def get_services():
    login = restlin.get_login()
    db = Database(login.username, login.password)
    response = db.get_services()
    return response

#CLIENT ROUTES
@app.put("/delete/clients")
def delete_client(id_: ID):
    login = restlin.get_login()
    db = Database(login.username, login.password)
    restlin.log_warning(f"Client deleted by: {login.username}")
    return db.delete_client(id_.id_)

@app.put("/update/clients")
def update_client(client: Clients):
    login = restlin.get_login()
    db = Database(login.username, login.password)
    restlin.log_info(f"Client {client.fio} data updated by: {login.username}")
    return db.update_client(client)

@app.put("/insert/clients")
def insert_client(client: Clients):
    login = restlin.get_login()
    db = Database(login.username, login.password)
    restlin.log_info(f"Added new client {client.fio} by: {login.username}")
    return db.insert_clients(client)


#SERVICE ROUTES
@app.put("/delete/services")
def delete_client(id_: ID):
    login = restlin.get_login()
    db = Database(login.username, login.password)
    restlin.log_warning(f"Service deleted by: {login.username}")
    return db.delete_service(id_.id_)

@app.put("/insert/services")
def insert_client(service: Services):
    login = restlin.get_login()
    db = Database(login.username, login.password)
    restlin.log_warning(f"Added new service {service.service} by: {login.username}")
    return db.insert_service(service)


#ROLE ROUTES
@app.put("/delete/role")
def delete_role(role: Login):
    login = restlin.get_login()
    db = Database(login.username, login.password)
    restlin.log_warning(f"Role deleted by: {login.username}")
    return db.delete_role(role.username)

@app.put("/insert/role")
def insert_role(role: Login):
    login = restlin.get_login()
    db = Database(login.username, login.password)
    restlin.log_warning(f"Added new role {role.username} by: {login.username}")
    return db.insert_role(role)

if __name__ == "__main__":
    restlin.start_unicorn()
