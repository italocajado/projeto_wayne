from sqlalchemy.sql import text

class RepositoryUsuario:
    def select_all():
        return text('SELECT * FROM TBL_USUARIO')

    def select_user(nm_usuario:str):
        return text("""
            SELECT tu.NM_USUARIO, tu.SENHA, tf.NVL_ACESSO 
            FROM TBL_USUARIO tu 
            INNER JOIN TBL_FUNCAO tf ON tu.ID_FUNCAO = tf.ID_FUNCAO  
            WHERE tu.NM_USUARIO = '{}'""".format(nm_usuario.upper())
        )

    def insert_user(dados:dict):
        query = text("INSERT INTO tbl_usuario (NM_USUARIO, CPF, SENHA, ID_FUNCAO) VALUES ('%s', '%s', '%s', %s)" % tuple(x for x in dados.values()))
        return query

    def alter_user(dados:dict):
        if dados['SENHA']:
            query = text("""
                UPDATE TBL_USUARIO 
                SET 
                    NM_USUARIO = '{NM_USUARIO}', 
                    CPF = '{CPF}', 
                    ID_FUNCAO = {ID_FUNCAO},
                    ALTERED_AT = '{ALTERED_AT}',
                    SENHA = '{SENHA}'
                WHERE ID_USUARIO = {ID_USUARIO}""".format(
                    NM_USUARIO = dados['NM_USUARIO'],
                    CPF = dados['CPF'],
                    ID_FUNCAO = dados['ID_FUNCAO'],
                    ALTERED_AT = dados['ALTERED_AT'],
                    SENHA = dados['SENHA'],
                    ID_USUARIO = dados['ID']
                )
            )
        else:
            query = text("""
                UPDATE TBL_USUARIO 
                SET 
                    NM_USUARIO = '{NM_USUARIO}', 
                    CPF = '{CPF}', 
                    ID_FUNCAO = {ID_FUNCAO},
                    ALTERED_AT = '{ALTERED_AT}'
                WHERE ID_USUARIO = {ID_USUARIO}""".format(
                    NM_USUARIO = dados['NM_USUARIO'],
                    CPF = dados['CPF'],
                    ID_FUNCAO = dados['ID_FUNCAO'],
                    ALTERED_AT = dados['ALTERED_AT'],
                    ID_USUARIO = dados['ID']
                ) 
            )
        return query

    def delete_user(id):
        query = text("DELETE FROM TBL_USUARIO WHERE ID_USUARIO = %s" % id)
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

    def alter_room(dados:dict):
        query = text("""
            UPDATE TBL_SALA
            SET 
                DE_SALA = '%s', 
                ID_SALA = %s,
                NVL_ACESSO = '%s'
            WHERE ID_SALA = %s""" % tuple(x for x in dados.values()))
        return query

    def delete_room(id):
        query = text("DELETE FROM TBL_SALA WHERE ID_SALA = %s" % id)
        return query

class RepositoryInventory:
    def select_all():
        return text('SELECT * FROM TBL_INVENTARIO')
    
    def insert_item(dados:dict):
        query = text("INSERT INTO tbl_inventario (DE_RECURSO, NR_SERIE, ID_SALA) VALUES ('%s', '%s', %s)" % tuple(x for x in dados.values()))
        return query
    
    def alter_item(dados:dict):
        query = text("""
            UPDATE TBL_INVENTARIO
            SET 
                DE_RECURSO = '%s', 
                NR_SERIE = '%s',
                ID_SALA = '%s',
                ALTERED_AT = '%s'
            WHERE ID_RECURSO = %s""" % tuple(x for x in dados.values()))
        return query
    
    def delete_item(id):
        query = text("DELETE FROM TBL_INVENTARIO WHERE ID_RECURSO = %s" % id)
        return query
