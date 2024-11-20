from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
from src.models.database.connection import db_connection_handler
from src.models.database.repository import RepositoryUsuario
from src.models.password_hash import HandlerPasswordHash
from sqlalchemy.sql import text

app = Flask(__name__)
CORS(app)

db_connection_handler.connect_to_db()
repository_usuario = RepositoryUsuario()
handler_password = HandlerPasswordHash()

if 'database.db' not in os.listdir(sys.path[0]):
    with db_connection_handler as db:
        with open('./init/schema.sql') as r:
            lista_querys = r.read().split(';')
            for e in lista_querys:
                db.execute(text(e))
        
####################   ROTAS  ####################  

@app.route('/', methods=['GET'])
def main():
    return "Hello World"

@app.route('/usuarios/', methods=['POST'])
def usuarios():
    response = None
    with db_connection_handler as db:
        response = db.execute(repository_usuario.select_all()).fetchall()
        print(response)
    return jsonify(response), 200

@app.route('/usuarios/add', methods=['POST'])
def adicionar_usuario():
    dados_usuario = request.json
    with db_connection_handler as db:
        # NM_USUARIO TEXT NOT NULL,
        # CPF TEXT,
        # SENHA TEXT NOT NULL,
        # ID_FUNCAO INTEGER NOT NULL,
        # CREATED_AT DATE DEFAULT (DATETIME('now')),
        # ALTERED_AT DATE,
        # FOREIGN KEY (ID_FUNCAO) REFERENCES TBL_FUNCAO(ID_FUNCAO)

        dados_usuario['SENHA'] = handler_password.gerar_hash(dados_usuario['SENHA'])

        

        response = db.execute(repository_usuario.select_all()).fetchall()
        print(response)

    return 'response', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)