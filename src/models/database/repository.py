from sqlalchemy.sql import text

class RepositoryUsuario:
    def __init__(self):
        self.__select_all = text('SELECT * FROM TBL_USUARIO')

    def select_all(self):
        return self.__select_all

