from sqlalchemy.sql import text

class RepositoryUsuario:
    def select_all():
        return text('SELECT * FROM TBL_USUARIO')

    def insert_user(dados:dict):
        query = text("INSERT INTO tbl_usuario (NM_USUARIO, CPF, SENHA, ID_FUNCAO) VALUES ('%s', '%s', '%s', %s)" % tuple(x for x in dados.values()))
        return query

    def alter_user(dados:dict):
        query = text("UPDATE TBL_USUARIO SET NM_USUARIO = '%s', CPF = '%s', ID_FUNCAO = %s WHERE ID_USUARIO = %s" % tuple(x for x in dados.values()))
        return query

class RepositoryFuncao:
    def select_all():
        return text('SELECT * FROM TBL_FUNCAO')

class RepositorySala:
    def select_all():
        return text('SELECT * FROM TBL_SALA')
    
    def insert_room(dados:dict):
        query = text("INSERT INTO tbl_sala (DE_SALA, NVL_ACESSO) VALUES ('%s', %s)" % tuple(x for x in dados.values()))
        return query

class RepositoryInventory:
    def select_all():
        return text('SELECT * FROM TBL_INVENTARIO')
    
    def insert_item(dados:dict):
        query = text("INSERT INTO tbl_inventario (DE_RECURSO, NR_SERIE, ID_SALA) VALUES ('%s', '%s', %s)" % tuple(x for x in dados.values()))
        return query
