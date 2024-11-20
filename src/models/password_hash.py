import bcrypt

class HandlerPasswordHash:
    def __init__(self):
        self.__senha = None
        self.__senha_hash = None

    def gerar_hash(senha):
        return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
    
    def verificar_senha(senha, hash):
        return bcrypt.checkpw(senha.encode('utf-8'), hash)