import psycopg2
import yaml
from models.models import Data, Response


class Database:

    def __init__(self, username, password):
        # READ CONFIGURATION FROM config FILE
        data = self.__get_config()

        # PARSE DATA FROM DICTIONARY
        self.__HOST = data['HOST']
        self.__DATABASE = data['DATABASE']
        self.__PORT = data['PORT']

        # CREATE CONNECTION
        self.__CONNECTION = psycopg2.connect(
            host=self.__HOST,
            port=self.__PORT,
            database=self.__DATABASE,

            user=username,
            password=password
        )

        # CREATE CURSOR
        self.__CURSOR = self.__CONNECTION.cursor()
        

    def __test(self):
        self.__CURSOR.execute("call update_live_status(2,2,1)")
        self.__CONNECTION.commit()

    def __get_config(self):
        with open('../configuration/database.config') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            print(data)
            return data

    def is_admin(self):
        self.__CURSOR.execute("SELECT is_super()")
        return self.__CURSOR.fetchone()[0]

    def get_data_for_managers(self):
        self.__CURSOR.execute("SELECT * FROM managers_view")
        data = self.__CURSOR.fetchall()
        self.__CURSOR.execute("SELECT * FROM managers_live_view")
        live = self.__CURSOR.fetchall()
        self.__CURSOR.execute("SELECT service FROM services ORDER BY id")
        services = self.__CURSOR.fetchall()
        organised_data = Data()
        index = 0
        response = Response()
        response.data = []
        response.services = []
        for service in services:
            response.services.append(service[0])
        for d in data:
            organised_data.statuses = []
            organised_data.name = d[0]
            organised_data.phone = d[1]
            organised_data.adress = d[2]
            organised_data.salary = d[3]
            for s in services:
                organised_data.statuses.append(live[index][0])
                index += 1
            response.data.append(organised_data)
            organised_data = Data()
        return response