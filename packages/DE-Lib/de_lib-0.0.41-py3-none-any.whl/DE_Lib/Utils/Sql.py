

class SQL:
    def __init__(self):
        ...

    @staticmethod
    def colunas_cursor(cursor) -> list:
        header = [head[0] for head in cursor.description]
        return header

    @staticmethod
    def Crud(sql: str = None, values: dict = None, conexao=None, commit: bool = True):
        msg, result, linhas_afetadas = None, [], 0
        try:
            if not isinstance(sql, str) or sql is None:
                raise Exception(f"""Comando sql não foi definido {sql}""")
            if conexao is None:
                raise Exception(f"""Conexão não foi informada {conexao}""")
            if not isinstance(values, dict):
                raise Exception(f"""Lista de valores não foi informada {values}""")
            cursor = conexao.cursor()
            cursor.execute(sql, values)
            linhas_afetadas = cursor.rowcount
            cursor.close()
            if commit:
                conexao.commit()
            msg = f"""Comando SQL executado com sucesso!"""
        except Exception as error:
            msg = f"""Falha ao tentar executar o comando SQL! Erro: {error}"""
            result = msg
        finally:
            result = {"linhas_afetadas": linhas_afetadas, "mensagem": msg, "sql": sql}
            return result

    @staticmethod
    def fromListDictToList(listDict, keyValue) -> list:
        result = None
        try:
            __list = []
            for n in range(len(listDict)):
                __list.append(listDict[n][keyValue])
            result = __list
        except Exception as error:
            result = error.args[0]
        finally:
            return result

    @staticmethod
    def ListToDict(colsname:list,  lst:list):
        msg, result = None, None
        try:
            result = []
            for n in range(len(lst)):
                result.append(dict(zip(colsname, lst[n])))
        except Exception as error:
            msg = error.args[0]
            result = msg
        finally:
            return result

    @staticmethod
    def CursorToDict(cursor) -> list:
        msg, result = None, None
        try:
            columnsName = [col[0] for col in cursor.description]
            result = []
            rows = cursor.fetchall()
            if len(rows) > 0:
                for row in rows:
                    result.append(dict(zip(columnsName, row)))
            else:
                result.append(dict.fromkeys(columnsName))
        except Exception as error:
            msg = error.args[0]
            result = msg
        finally:
            return result