import psycopg2
import yaml
from models.models import Data, Response, Managers, Clients, Services, Login
from logger.logger import Logger


class Database:

    def __init__(self, username, password):
        # READ CONFIGURATION FROM config FILE
        self.__CONFIG = "../config/config.config"

        # PARSE DATA FROM DICTIONARY
        self.__HOST = ''
        self.__DATABASE = ''
        self.__PORT = ''
        self.__get_config()

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
        
        #LOGGER
        self.__LOGGER = Logger("database")
        self.__LOGGER.log_info(f"Established new connection to database by {username}.")

    def __get_config(self):
        with open(self.__CONFIG, 'r') as stream:
            db = yaml.load(stream, Loader=yaml.FullLoader)['DATABASE']
            self.__HOST = db['HOST']
            self.__PORT = db['PORT']
            self.__DATABASE = db['DATABASE']


    def __get_ids_for_update(self, clientname, clientnumber, servicename, statusname):
        self.__CURSOR.execute(f"SELECT * FROM get_id_for_update('{clientname}', '{clientnumber}', '{servicename}', '{statusname}')")
        return self.__CURSOR.fetchone()

    def update_client_live(self, clientname, clientnumber, servicename, statusname):
        try:
            data = self.__get_ids_for_update(clientname, clientnumber, servicename, statusname)
            self.__CURSOR.execute(f"call update_live_status({data[0]}, {data[1]}, {data[2]})")
            self.__CONNECTION.commit()
        except Exception as e:
            self.__LOGGER.log_error(f"Update client live raised error: {e}")


    def is_admin(self):
        self.__CURSOR.execute("SELECT is_super()")
        return self.__CURSOR.fetchone()[0]

    def get_data_for_managers(self):
        try:
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
                organised_data.name   = d[0]
                organised_data.phone  = d[1]
                organised_data.adress = d[2]
                organised_data.salary = d[3]
                for s in services:
                    organised_data.statuses.append(live[index][0])
                    index += 1
                response.data.append(organised_data)
                organised_data = Data()
        except Exception as e:
            self.__LOGGER.log_error(f"Get data for managers raised error: {e}")
        return response

    def get_managers(self):
        try:
            self.__CURSOR.execute("SELECT * FROM administrator_user_view")
            response = []
            manager = Managers()
            managers = self.__CURSOR.fetchall()
            for m in managers:
                manager.username = m[0]
                response.append(manager)
                manager = Managers()
        except Exception as e:
            self.__LOGGER.log_error(f"Get managers raised error: {e}")
        return response

    def get_clients(self):
        try:
            self.__CURSOR.execute("SELECT * FROM administrator_client_view")
            clients = self.__CURSOR.fetchall()
            response = []
            client = Clients()
            for c in clients:
                client.id_        = c[0]
                client.fio        = c[1]
                client.tel        = c[2]
                client.job        = c[3]
                client.homeadress = c[4]
                client.salary     = c[5]
                client.call_back  = c[6]
                response.append(client)
                client = Clients()
        except Exception as e:
            self.__LOGGER.log_error(f"Get clients raised error: {e}")

        return response

    def get_services(self):
        try:
            self.__CURSOR.execute("SELECT * FROM administrator_service_view")
            services = self.__CURSOR.fetchall()
            response = []
            service = Services()
            for s in services:
                service.id_                 = s[0]
                service.service             = s[1]
                service.service_description = s[2]
                response.append(service)
                service = Services()
        except Exception as e:
            self.__LOGGER.log_error(f"Get services raised error: {e}")
        return response


    def delete_client(self, id_):
        try:
            self.__CURSOR.execute(f"call delete_client({id_})")
            self.__CONNECTION.commit()
        except Exception as e:
            self.__LOGGER.log_error(f"Delete client raised error: {e}")
            return False
        return True


    def update_client(self, client: Clients):
        try:
            cli = client.dict()
            query = f"call update_client(client_id_p=>{client.id_}"
            for c in cli.keys():
                if(cli[c] and c != "id_" and c != "call_back" and c != "salary"):
                    query += f",{c}_p=>'{cli[c]}'"
                elif(cli[c] and c == "salary" or c == "call_back"):
                    query += f",{c}_p=>{cli[c]}"
            query += ")"
            self.__CURSOR.execute(query)
            self.__CONNECTION.commit()
        except Exception as e:
            self.__LOGGER.log_error(f"Update client raised error: {e}")
            return False
        return True

    def insert_clients(self, client: Clients):
        try:
            self.__CURSOR.execute(f"call insert_client('{client.fio}','{client.tel}','{client.job}', '{client.homeadress}', '{client.salary}')")
            self.__CONNECTION.commit()
        except Exception as e:
            self.__LOGGER.log_error(f"Insert client raised error: {e}")
            return False
        return True

    def delete_service(self, id_):
        try:
            self.__CURSOR.execute(f"call delete_service({id_})")
            self.__CONNECTION.commit()
        except Exception as e:
            self.__LOGGER.log_error(f"Delete service raised error: {e}")
            return False
        return True

    def insert_service(self, service: Services):
        try:
            self.__CURSOR.execute(f"select insert_service('{service.service}','{service.service_description}')")
            self.__CONNECTION.commit()
        except Exception as e:
            self.__LOGGER.log_error(f"Insert service raised error: {e}")
            return False
        return True

    def delete_role(self, username):
        try:
            self.__CURSOR.execute(f"call delete_user('{username}')")
            self.__CONNECTION.commit()
        except Exception as e:
            self.__LOGGER.log_error(f"Delete role raised error: {e}")
            return False
        return True
    
    def insert_role(self, login: Login):
        try:
            self.__CURSOR.execute(f"call add_user('{login.username}', '{login.password}')")
            self.__CONNECTION.commit()
        except Exception as e:
            self.__LOGGER.log_error(f"Insert role raised error: {e}")
            return False
        return True
