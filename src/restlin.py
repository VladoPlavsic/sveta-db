import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import Database
from receiver import amqp__ini__
from sender import sender
from  models.models import Login, Response, Data, ClientUpdates, Managers, Clients, Services, ID
import requests
import json
import threading
import sys

HOST = 'localhost'
PORT = 1337
app = FastAPI()
_login = Login()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# POST ROUTE FOR CREATING A USER
@app.post("/user")
def log_in(login: Login):

    print(f"Recived post with username {login.username} and password {login.password}")
    _login.username = login.username
    _login.password = login.password
    response = Response()

    try:
        db = Database(login.username, login.password)
        response = db.get_data_for_managers()
        if(db.is_admin()):
            response.admin = True
        else:
            response.admin = False
    except Exception as e:
        print("Exception raised: ", e)
        response.error = True
    return response

@app.put("/update")
def update_user(client_updates: ClientUpdates):
    print(client_updates)
    db = Database(client_updates.username, client_updates.password)
    for s in client_updates.updated:
        if s.update:
            if s.status:
                db.update_client_live(clientname=client_updates.clientname, clientnumber=client_updates.clientnumber,servicename=s.service,statusname=s.status)
    sender.send("Updated client", "sync")
    return True

@app.get("/managers")
def get_managers():
    db = Database(_login.username, _login.password)
    response = db.get_managers()
    return response

@app.get("/clients")
def get_clients():
    db = Database(_login.username, _login.password)
    response = db.get_clients()
    return response

@app.get("/services")
def get_services():
    db = Database(_login.username, _login.password)
    response = db.get_services()
    return response

@app.put("/delete")
def delete_client(id_: ID):
    db = Database(_login.username, _login.password)
    return db.delete_client(id_.id_)

@app.put("/update/client")
def update_client(client: Clients):
    db = Database(_login.username, _login.password)
    db.update_client(client)
    print(f"Got update request with {client}")
    return True

def start_unicorn(app, host, port):
    uvicorn.run(app, host=host, port=port, log_level='error')

def start_amqp():

    print(f"Started amqp")

    def amqp_callback(ch, method, properties, body):
        message = json.loads(body)["message"]
        logger.log_info(f"DATA RECEIVED WITH MESSAGE {message}")

        if(message == "connect" or message == "disconnect"):
            requests.put('http://localhost:1337/tower', data=body)
        if(message == "attack" or message == "shield"):
            requests.put('http://localhost:1337/defender', data=body)

    amqp__ini__(routing_key="Restlin", amqp_callback=amqp_callback)


if __name__ == "__main__":
    amqp = threading.Thread(target=start_amqp)
    amqp.start()
    start_unicorn(app, HOST, PORT)
