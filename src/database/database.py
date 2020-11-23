import psycopg2
import yaml


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
        self.__test()

    def __test(self):
        self.__CURSOR.execute("SELECT * FROM books")
        print(self.__CURSOR.fetchall())

    def __get_config(self):
        with open('../configuration/database.config') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            print(data)
            return data


def test():
    db = Database('worker2', 'worker2')


if __name__ == "__main__":
    test()
