import jaydebeapi as jdb
import jpype as jp
import os
import json

from DE_Lib.Utils import Generic

gen = Generic.GENERIC()

class CACHE:
    def __init__(self):
        self._connection_is_valid = None
        self._nome_database = None
        self._cnn = None
        self.__database_error = None

    def Connect(self, string_connect):
        """
        Conexao com a base CACHÉ (Intersystem)
        O arquivo "CacheDB.jar" --> Tem que estar na mesma pasta de da lib ou ter o seu
        caminho completo declarado na chamada da funcao
        :param string_connect:
                    "database": "cache",
                    "name_conection": "Nome da conexão para melhor identicacao",
                    "driver": str: default = "CacheDB.jar",
                    "user": str: Nome do usuario,
                    "pwd": str: senha do usuario,
                    "host": str: Nome do host (Url ou IP),
                    "port": str: Numero da porta --> default = "1972",
                    "instance": str: <Nome da instanciaa ser conectada>
        :return:
        """
        msg, result = None, None
        try:
            if string_connect["database"] == "":
                string_connect["database"] = "cache"
            if string_connect["driver_conexao"] == "":
                string_connect["driver_conexao"] = "CacheDB.jar"
            if string_connect["port"] == "":
                string_connect["port"] = "1972"
            jarODBC = os.path.join(string_connect["driver_library"], string_connect["driver_conexao"])
            JHOME = jp.getDefaultJVMPath()
            jp.startJVM(JHOME, f"""-Djava.class.path={jarODBC}""")
            __driver = "com.intersys.jdbc.CacheDriver"
            __usr = string_connect["user"]
            __pwd = string_connect["pwd"]
            __host = string_connect["host"]
            __port = string_connect["port"]
            __namespace = string_connect["instance"]
            __url = f"""jdbc:Cache://{__host}:{__port}/{__namespace}"""
            result = jdb.connect(__driver, __url, [__usr, __pwd])
            self._connection_is_valid = True
            self._cnn = result
            self._database_error = f"""{json.dumps(string_connect, indent=4).replace(string_connect["pwd"], "******")}\nConexao bem sucedida!"""
            self._nome_database = gen.nvl(string_connect["database"], "")
        except Exception as error:
            msg = f"""{json.dumps(string_connect, indent=4).replace(string_connect["pwd"], "******")}\nFalha ao tentar se conectar com o banco de dados CACHÉ (intersystem)\nException Error: {error} """
            result = msg
            self._connection_is_valid = False
            self._database_error = msg
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
        return self._database_error