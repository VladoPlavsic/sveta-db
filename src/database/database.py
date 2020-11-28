import psycopg2
import yaml
from models.models import Data, Response, ClientUpdates, Managers, Clients, Services


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


    def __get_ids_for_update(self, clientname, clientnumber, servicename, statusname):
        self.__CURSOR.execute(f"SELECT * FROM get_id_for_update('{clientname}', '{clientnumber}', '{servicename}', '{statusname}')")
        return self.__CURSOR.fetchone()

    def update_client_live(self, clientname, clientnumber, servicename, statusname):
        data = self.__get_ids_for_update(clientname, clientnumber, servicename, statusname)
        self.__CURSOR.execute(f"call update_live_status({data[0]}, {data[1]}, {data[2]})")
        self.__CONNECTION.commit()

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
            organised_data.name   = d[0]
            organised_data.phone  = d[1]
            organised_data.adress = d[2]
            organised_data.salary = d[3]
            for s in services:
                organised_data.statuses.append(live[index][0])
                index += 1
            response.data.append(organised_data)
            organised_data = Data()
        return response

    def get_managers(self):
        self.__CURSOR.execute("SELECT * FROM administrator_user_view")
        response = []
        manager = Managers()
        managers = self.__CURSOR.fetchall()
        for m in managers:
            manager.username = m[0]
            response.append(manager)
            manager = Managers()

        return response

    def get_clients(self):
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

        return response

    def get_services(self):
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

        return response


    def delete_client(self, id_):
        try:
            self.__CURSOR.execute(f"call delete_client({id_})")
            self.__CONNECTION.commit()
        except Exception as e:
            return False
        return True

    def update_client(self, client: Clients):
        self.__CURSOR.execute(f"call update_client({client.id_},'{client.fio or 'NULL'}','{client.tel or 'NULL'}','{client.job or 'NULL'}','{client.homeadress or 'NULL'}',{client.salary or 'NULL'},{client.call_back})")
        self.__CONNECTION.commit()

def main():
    db = Database("admin", "admin")
    db.update_client(1)

if __name__ == "__main__":
    main()