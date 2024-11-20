from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
from src.models.database.connection import db_connection_handler
from src.models.database.repository import RepositoryUsuario, RepositoryFuncao,RepositorySala,RepositoryInventory
from src.models.password_hash import HandlerPasswordHash
from sqlalchemy.sql import text

app = Flask(__name__)
CORS(app)

db_connection_handler.connect_to_db()
repository_usuario = RepositoryUsuario
repository_funcao = RepositoryFuncao
repository_sala = RepositorySala
repository_inventory = RepositoryInventory
handler_password = HandlerPasswordHash

if 'database.db' not in os.listdir(sys.path[0]):
    with db_connection_handler as db:
        with open('./init/schema.sql') as r:
            lista_querys = r.read().split(';')
            for e in lista_querys:
                db.begin() if not db.in_transaction() else None
                db.execute(text(e))
                db.commit()
            print('Banco de Dados Materializado')

with db_connection_handler as db:
    if len(db.execute(repository_funcao.select_all()).fetchall()) == 0:
        with open('./init/insert.sql') as r:
            lista_querys = r.read().split(';')
            for e in lista_querys:
                db.begin() if not db.in_transaction() else None
                db.execute(text(e))
                db.commit()
            print('Dados iniciais inseridos')

####################   ROTAS  ####################  

@app.route('/', methods=['GET'])
def main():
    return "Hello World"

@app.route('/usuarios', methods=['GET'])
def usuarios():
    with db_connection_handler as db:
        response = db.execute(repository_usuario.select_all()).fetchall()
        response_dict = [{
            'ID_USUARIO': e[0],
            'NM_USUARIO': e[1],
            'CPF': e[2],
            'NVL_ACESSO': e[4],
            'CREATED_AT': e[5],
            'ALTERED_AT': e[6]
        } for e in response]
    return jsonify(response_dict), 200

@app.route('/usuarios/add', methods=['POST'])
def adicionar_usuario():
    if not request.is_json:
        return jsonify({"error": "Formato inválido. Necessário o parâmetro Header = Content-Type: application/json."}), 400
    
    dados_usuario = request.json

    if len(dados_usuario) != 4:
        return jsonify({"error": "Formato de payload inválido. Necessário 4 campos no payload (NM_USUARIO, CPF, SENHA, ID_FUNCAO)."}), 400
    
    if not dados_usuario.get('NM_USUARIO') or not dados_usuario.get('CPF') or not dados_usuario.get('SENHA') or not dados_usuario.get('ID_FUNCAO'):
        list = [x for x in ('NM_USUARIO','CPF','SENHA','ID_FUNCAO') if x not in dados_usuario]

        return jsonify({"error": "Formato de payload inválido. Campos faltantes: {}".format(list)}), 400

    dados_usuario['SENHA'] = handler_password.gerar_hash(str(dados_usuario['SENHA']).encode('utf-8')).decode('utf-8')

    with db_connection_handler as db:
        db.begin() if not db.in_transaction() else None
        db.execute(repository_usuario.insert_user(dados_usuario))
        db.commit()
        
    return jsonify({'message': 'Usuário cadastrado com sucesso!', 'dados': dados_usuario}), 200

@app.route('/usuarios/alter/<id>', methods=['POST'])
def alterar_usuario(id):
    if not request.is_json:
        return jsonify({"error": "Formato inválido. Necessário o parâmetro Header = Content-Type: application/json."}), 400
    
    dados_usuario = request.json

    if len(dados_usuario) != 3:
        return jsonify({"error": "Formato de payload inválido. Necessário 3 campos no payload (NM_USUARIO, CPF, ID_FUNCAO)."}), 400
    
    if not dados_usuario.get('NM_USUARIO') or not dados_usuario.get('CPF') or not dados_usuario.get('ID_FUNCAO'):
        list = [x for x in ('NM_USUARIO','CPF','ID_FUNCAO') if x not in dados_usuario]

        return jsonify({"error": "Formato de payload inválido. Campos faltantes: {}".format(list)}), 400

    dados_usuario['ID'] = id

    with db_connection_handler as db:
        db.begin() if not db.in_transaction() else None
        result = db.execute(repository_usuario.alter_user(dados_usuario))
        db.commit()
    
    if result.rowcount == 0:
        return jsonify({'error': 'ID_USUARIO não encontrado.', 'dados': dados_usuario}), 404
    else:
        return jsonify({'message': 'Usuário alterado com sucesso!', 'dados': dados_usuario}), 200

@app.route('/funcoes', methods=['GET'])
def funcoes():
    response = None
    with db_connection_handler as db:
        response = db.execute(repository_funcao.select_all()).fetchall()
        response_dict = [{'Função': j[1], 'Nível Acesso': j[2]}  for i,j in enumerate(response)]
    return jsonify(response_dict), 200

@app.route('/salas', methods=['GET'])
def salas():
    with db_connection_handler as db:
        response = db.execute(repository_sala.select_all()).fetchall()
        response_dict = [{
            'ID_SALA': e[0],
            'DE_SALA': e[1],
            'NVL_ACESSO': e[2],
            'CREATED_AT': e[3],
            'ALTERED_AT': e[4]
        } for e in response]
    return jsonify(response_dict), 200

@app.route('/salas/add', methods=['POST'])
def adicionar_sala():
    if not request.is_json:
        return jsonify({"error": "Formato inválido. Necessário o parâmetro Header = Content-Type: application/json."}), 400
    
    dados_sala = request.json

    if len(dados_sala) != 2:
        return jsonify({"error": "Formato de payload inválido. Necessário 2 campos no payload (DE_SALA, NVL_ACESSO)."}), 400
    
    if not dados_sala.get('DE_SALA') or not dados_sala.get('NVL_ACESSO'):
        list = [x for x in ('DE_SALA','NVL_ACESSO') if x not in dados_sala]

        return jsonify({"error": "Formato de payload inválido. Campos faltantes: {}".format(list)}), 400
        
    with db_connection_handler as db:
        db.begin() if not db.in_transaction() else None
        db.execute(repository_sala.insert_room(dados_sala))
        db.commit()
        
    return jsonify({'message': 'Sala cadastrada com sucesso!', 'dados': dados_sala}), 200

@app.route('/salas/alter/<id>', methods=['POST'])
def alterar_sala(id):
    if not request.is_json:
        return jsonify({"error": "Formato inválido. Necessário o parâmetro Header = Content-Type: application/json."}), 400
    
    dados_usuario = request.json

    if len(dados_usuario) != 3:
        return jsonify({"error": "Formato de payload inválido. Necessário 3 campos no payload (NM_USUARIO, CPF, ID_FUNCAO)."}), 400
    
    if not dados_usuario.get('NM_USUARIO') or not dados_usuario.get('CPF') or not dados_usuario.get('ID_FUNCAO'):
        list = [x for x in ('NM_USUARIO','CPF','ID_FUNCAO') if x not in dados_usuario]

        return jsonify({"error": "Formato de payload inválido. Campos faltantes: {}".format(list)}), 400

    dados_usuario['ID'] = id

    with db_connection_handler as db:
        db.begin() if not db.in_transaction() else None
        result = db.execute(repository_usuario.alter_user(dados_usuario))
        db.commit()
    
    if result.rowcount == 0:
        return jsonify({'error': 'ID_USUARIO não encontrado.', 'dados': dados_usuario}), 404
    else:
        return jsonify({'message': 'Usuário alterado com sucesso!', 'dados': dados_usuario}), 200


@app.route('/inventario', methods=['GET'])
def inventario():
    with db_connection_handler as db:
        response = db.execute(repository_inventory.select_all()).fetchall()
        response_dict = [{
            'ID_RECURSO': e[0],
            'DE_RECURSO': e[1],
            'NR_SERIE': e[2],
            'ID_SALA': e[3],
            'CREATED_AT': e[4],
            'ALTERED_AT': e[5]
        } for e in response]
    return jsonify(response_dict), 200

@app.route('/inventario/add', methods=['POST'])
def adicionar_item():
    if not request.is_json:
        return jsonify({"error": "Formato inválido. Necessário o parâmetro Header = Content-Type: application/json."}), 400
    
    dados_item = request.json

    if len(dados_item) != 3:
        return jsonify({"error": "Formato de payload inválido. Necessário 3 campos no payload (DE_RECURSO,NR_SERIE,ID_SALA)."}), 400
    
    if not dados_item.get('DE_RECURSO') or not dados_item.get('NR_SERIE') or not dados_item.get('ID_SALA'):
        list = [x for x in ('DE_RECURSO','NR_SERIE','ID_SALA') if x not in dados_item]

        return jsonify({"error": "Formato de payload inválido. Campos faltantes: {}".format(list)}), 400

    with db_connection_handler as db:
        db.begin() if not db.in_transaction() else None
        db.execute(repository_inventory.insert_item(dados_item))
        db.commit()
        
    return jsonify({'message': 'Usuário cadastrado com sucesso!', 'dados': dados_item}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
