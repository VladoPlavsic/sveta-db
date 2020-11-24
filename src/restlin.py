import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import Database
from  models.models import Login, Response, Data
import requests
import json
import threading
import sys

HOST = 'localhost'
PORT = 1337
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# POST ROUTE FOR CREATING A USER


@app.post("/user")
def create_user(login: Login):

    print(f"Recived post with username {login.username} and password {login.password}")

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


def start_unicorn(app, host, port):
    uvicorn.run(app, host=host, port=port, log_level='error')

'''def start_amqp():

    print(f"Started amqp")

    def amqp_callback(ch, method, properties, body):
        message = json.loads(body)["message"]
        logger.log_info(f"DATA RECEIVED WITH MESSAGE {message}")

        if(message == "connect" or message == "disconnect"):
            requests.put('http://localhost:1337/tower', data=body)
        if(message == "attack" or message == "shield"):
            requests.put('http://localhost:1337/defender', data=body)

    amqp__ini__(routing_key="Restlin", amqp_callback=amqp_callback)

'''
if __name__ == "__main__":
    #amqp = threading.Thread(target=start_amqp)
    #amqp.start()
    start_unicorn(app, HOST, PORT)
