import sqlite3 as sq3
import sqlalchemy as sqa
import os
import json

from DE_Lib.Utils import Generic

gen = Generic.GENERIC()

class SQLITE:
    def __init__(self):
        self._connection_is_valid = None
        self._nome_database = None
        self._cnn = None
        self.__database_error = None

    def Connect(self, conn: dict, **kwargs):
        msg, result = None, True
        try:
            __file = os.path.join(conn["host"], conn["instance"])
            if os.path.isfile(__file):
                if "check_same_thread" in kwargs.keys():
                    __check_same_thread = kwargs.get("check_same_thread")
                else:
                    __check_same_thread = True

                #__conn = None
                if not conn["driver_conexao"]:
                    __conn = sq3.connect(__file, check_same_thread=__check_same_thread)
                elif conn["driver_conexao"].upper() == "SQLALCHEMY":
                    engine = sqa.create_engine(f"""sqlite:///{__file}""")
                    __conn = engine.connect()
                else:
                    ...
                    # driver nativo sqlite

            self._connection_is_valid = True
            self._cnn = __conn
            self._nome_database = gen.nvl(conn["database"], "SQLite")
            self.__database_driver = conn["driver_conexao"]
            self.__database_error = result
        except Exception as error:
            msg = f"""{json.dumps(conn, indent=4).replace(conn["password"], "******")}\nFalha ao tentar se conectar com o banco de dados SQLite\nException Error: {error} """
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
        return self._nome_database.upper()

    @property
    def DATABASE_ERROR(self):
        return self.__database_error

    @property
    def DATABASE_DRIVER(self):
        return self.__database_driver

    @DATABASE_DRIVER.setter
    def DATABASE_DRIVER(self, value):
        self._DATABASE_DRIVER = value