import mysql.connector as mysql
import pymysql
import sqlalchemy as sqa
import json

from DE_Lib.Utils import Generic

gen = Generic.GENERIC()

class MYSQL:
    def __init__(self):
        self._connection_is_valid = None
        self._nome_database = None
        self.__database_driver = None
        self._cnn = None
        self.__database_error = None

    def Connect(self, conn: dict):
        msg, result = None, True
        try:
            # Efetuando a conexao com a instancia do BANCO
            __conn = None
            if conn["driver_conexao"].upper() == "SQLALCHEMY":
                __dns = f"""{conn["database"].lower()}+pymysql://{conn["username"]}:{conn["password"]}@{conn["host"]}:{conn["port"]}/{conn["instance"]}"""
                __engine = sqa.create_engine(url=__dns)
                __conn = __engine.connect().connection
                #__conn = __conn.connection
            elif conn["driver_conexao"].upper() == "MYSQL":
                __conn = mysql.connect(user=conn["username"], password=conn["password"], database=conn["instance"], host=conn["host"])
            elif conn["driver_conexao"].upper() == "PYMYSQL":
                __conn = pymysql.connect(user=conn["username"], password=conn["password"], database=conn["instance"], host=conn["host"])#, cursorclass=pymysql.cursors.DictCursor)
            self._connection_is_valid = True
            self._nome_database = gen.nvl(conn["database"], "")
            self.__database_driver = conn["driver_conexao"]
            self._cnn = __conn
            self.__database_error = result
            result = True
        except Exception as error:
            msg = f"""{json.dumps(conn, indent=4).replace(conn["password"], "******")}\nFalha ao tentar se conectar com o banco de dados MYSQL\nException Error: {error} """
            result = msg
            self._connection_is_valid = False
            self.__database_error = msg
        finally:
            return result

    @property
    def CONNECTION(self):
        return self._cnn

    @property
    def CONNECTION_VALID(self):
        return self._connection_is_valid

    @property
    def NOME_DATABASE(self):
        return self._nome_database

    @property
    def DATABASE_ERROR(self):
        return self.__database_error

    @property
    def DATABASE_DRIVER(self):
        return self.__database_driver

    @DATABASE_DRIVER.setter
    def DATABASE_DRIVER(self, value):
        self._DATABASE_DRIVER = value