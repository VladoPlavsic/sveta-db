import psycopg2
import psycopg2.extras
import yaml
from models.models import Data, Response, Login, Drivers, Vehicles, Drives, PostVehicle, PostDriver, PostDrive, Managers, PostManager
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
        try:
            self.__CONNECTION = psycopg2.connect(
                host=self.__HOST,
                port=self.__PORT,
                database=self.__DATABASE,
                user=username,
                password=password
            )
        except Exception as e:
            print(f"Got exception trying to connect:\n {e}")

        # CREATE CURSOR
        self.__CURSOR = self.__CONNECTION.cursor(cursor_factory = psycopg2.extras.DictCursor)
        
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

    def get_managers(self, branch_id):
        try:
            self.__CURSOR.execute(f"SELECT * FROM get_managers_in_branch('branch{branch_id}')")
            managers = self.__CURSOR.fetchall()
            m = Managers()
            response = []
            for manager in managers:
                m.name = manager[0]
                m.oid = manager[1]
                response.append(m)
                m = Managers()
            return response
        except Exception as e:
            self.__LOGGER.log_error(f"Get managers raised error: {e}")
            return None

    def get_drivers(self, branch):
        try:
            self.__CURSOR.execute(f"SELECT * FROM branch{branch}_drivers_view")
            drivers = self.__CURSOR.fetchall()
            d = Drivers()
            response = []
            for driver in drivers:
                d.id = driver[0]
                d.fio = driver[1]
                d.driving_licence = driver[2]
                d.earnings = driver[3]
                d.status = driver[4]
                response.append(d)
                d = Drivers()
            return response
        except Exception as e:
            self.__LOGGER.log_error(f"Get drivers raised error: {e}")
            return None
            
    def get_vehicles(self, branch):
        try:
            self.__CURSOR.execute(f"SELECT * FROM branch{branch}_vehicles_view")
            vehicles = self.__CURSOR.fetchall()
            v = Vehicles()
            response = []
            for vehicle in vehicles:
                v.id = vehicle[0]
                v.mark = vehicle[1]
                v.carry_capacity = vehicle[2]
                v.status = vehicle[3]
                v.driver_id = vehicle[4]
                response.append(v)
                v = Vehicles()
            return response
        except Exception as e:
            self.__LOGGER.log_error(f"Get vehicles raised error: {e}")
            return None

    def _build_response_from_drives(self, drives):
        d = Drives()
        response = []
        for drive in drives:
            d.id = drive[0]
            d.driver_id = drive[1]
            d.vehicles_id = drive[2]
            d.cargo_weight = drive[3]
            d.destination = drive[4]
            d.destination_distance = drive[5]
            d.price = drive[6]
            response.append(d)
            d = Drives()
        return response

    def get_drives(self, branch):
        try:
            self.__CURSOR.execute(f"SELECT * FROM branch{branch}_active_drives_view")
            active_drives = self.__CURSOR.fetchall()
            self.__CURSOR.execute(f"SELECT * FROM branch{branch}_upcoming_drives_view")
            upcoming_drives = self.__CURSOR.fetchall()
            self.__CURSOR.execute(f"SELECT * FROM branch{branch}_history_drives_view")
            history_drives = self.__CURSOR.fetchall()
            response = {
                "upcoming": self._build_response_from_drives(upcoming_drives),
                "active": self._build_response_from_drives(active_drives), 
                "history": self._build_response_from_drives(history_drives)
                }
            return response
        except Exception as e:
            self.__LOGGER.log_error(f"Get drives raised error: {e}")
            return None
            

    def get_group(self): 
        try:
            self.__CURSOR.execute(f"SELECT * FROM user_group()")
            group = self.__CURSOR.fetchone()
            return group[0]
        except Exception as e:
            self.__LOGGER.log_error(f"Get group raised error: {e}")
            return None
            
    def add_driver(self, driver: PostDriver, branch_id):
        try:
            self.__CURSOR.execute(f"CALL branch{branch_id}.insert_driver('{driver.fio}', '{driver.driving_licence}')")
            self.__CONNECTION.commit()
            return True
        except Exception as e:
            self.__LOGGER.log_error(f"Insert vehicle raised error: {e}")
            return False

    def add_vehicle(self, vehicle: PostVehicle, branch_id):
        try:
            self.__CURSOR.execute(f"CALL branch{branch_id}.insert_vehicle('{vehicle.mark}', '{vehicle.carry_capacity}', {vehicle.driver_id})")
            self.__CONNECTION.commit()
            return True
        except Exception as e:
            self.__LOGGER.log_error(f"Insert vehicle raised error: {e}")
            return False

    def add_drive(self, drive: PostDrive, branch_id):
        try:
            self.__CURSOR.execute(f"SELECT branch{branch_id}.insert_drive({drive.driver_id}, {drive.vehicles_id}, {drive.cargo_weight}, '{drive.destination}', {drive.destination_distance}, {drive.price})")
            self.__CONNECTION.commit()
            return True
        except Exception as e:
            self.__LOGGER.log_error(f"Insert drive raised error: {e}")
            return False

    def delete_driver(self, driver_id, branch_id):
        try:
            self.__CURSOR.execute(f"SELECT branch{branch_id}.delete_driver({driver_id})")
            self.__CONNECTION.commit()
            return True
        except Exception as e:
            self.__LOGGER.log_error(f"Delete driver raised error: {e}")
            return False

    def delete_vehicle(self, vehicles_id, branch_id):
        try:
            self.__CURSOR.execute(f"SELECT branch{branch_id}.delete_vehicle({vehicles_id})")
            self.__CONNECTION.commit()
            return True
        except Exception as e:
            self.__LOGGER.log_error(f"Delete driver raised error: {e}")
            return False

    def delete_drive(self, drive_id, branch_id):
        try:
            self.__CURSOR.execute(f"SELECT branch{branch_id}.delete_drive({drive_id})")
            self.__CONNECTION.commit()
            return True
        except Exception as e:
            self.__LOGGER.log_error(f"Delete driver raised error: {e}")
            return False

    def set_drive_active(self, drive_id, branch_id):
        try:
            self.__CURSOR.execute(f"SELECT branch{branch_id}.set_drive_active({drive_id})")
            self.__CONNECTION.commit()
            return True
        except Exception as e:
            self.__LOGGER.log_error(f"Delete driver raised error: {e}")
            return False

    def set_drive_finished(self, drive_id, branch_id):
        try:
            self.__CURSOR.execute(f"SELECT branch{branch_id}.finish_drive({drive_id})")
            self.__CONNECTION.commit()
            return True
        except Exception as e:
            self.__LOGGER.log_error(f"Delete driver raised error: {e}")
            return False

    def delete_role(self, username):
        try:
            self.__CURSOR.execute(f"call delete_user('{username}')")
            self.__CONNECTION.commit()
        except Exception as e:
            self.__LOGGER.log_error(f"Delete role raised error: {e}")
            return False
        return True
    
    def add_manager(self, manager: PostManager, branch_id):
        try:
            self.__CURSOR.execute(f"call add_user('{manager.name}', '{manager.password}', 'branch{branch_id}')")
            self.__CONNECTION.commit()
        except Exception as e:
            self.__LOGGER.log_error(f"Insert role raised error: {e}")
            return False
        return True
