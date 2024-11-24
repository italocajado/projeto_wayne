import os
import sys
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy.sql import text
from sqlite3 import IntegrityError
from src.models.database.connection import db_connection_handler
from src.models.database.repository import RepositoryUsuario, RepositoryFuncao,RepositorySala,RepositoryInventory
from src.models.password_hash import HandlerPasswordHash

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

###### LOGIN ######
@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"error": "Formato inválido. Necessário o parâmetro Header = Content-Type: application/json."}), 400
    
    dados_usuario = request.json

    if len(dados_usuario) != 2:
        return jsonify({"error": "Formato de payload inválido. Necessário 2 campos no payload (NM_USUARIO, SENHA)."}), 

    if not dados_usuario.get('NM_USUARIO') or not dados_usuario.get('SENHA'):
        list = [x for x in ('NM_USUARIO','SENHA') if x not in dados_usuario]

        return jsonify({"error": "Formato de payload inválido. Campos faltantes: {}".format(list)}), 400

    with db_connection_handler as db:
        dados_usuario_base = db.execute(repository_usuario.select_user(dados_usuario['NM_USUARIO'])).fetchall()
    
    if len(dados_usuario_base) == 0:
        return {'Error': 'Usuário ou senha inválido.'}, 404
    elif not handler_password.verificar_senha(str(dados_usuario['SENHA']).encode('utf-8'),dados_usuario_base[0][1].encode('utf-8')):
        return {'Error': 'Usuário ou senha inválido.'}, 404
    elif handler_password.verificar_senha(str(dados_usuario['SENHA']).encode('utf-8'),dados_usuario_base[0][1].encode('utf-8')):
        return jsonify({
            'status':'Usuário logado com sucesso!', 
            'usuario': dados_usuario_base[0][0], 
            'NVL_ACESSO': dados_usuario_base[0][2]
        }), 200 

###### USUÁRIOS ######
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
        try:
            db.begin() if not db.in_transaction() else None
            db.execute(repository_usuario.insert_user(dados_usuario))
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
            return {'Error': 'Houve um erro no banco de dados.'}, 400
        
    return jsonify({
        'message': 'Usuário cadastrado com sucesso!',
        'dados': {
            'CPF':dados_usuario['CPF'], 
            'NOME':dados_usuario['NM_USUARIO'],
            'ID_FUNCAO':dados_usuario['ID_FUNCAO']
        }
    }), 200

@app.route('/usuarios/alter/<id>', methods=['POST'])
def alterar_usuario(id):
    if not request.is_json:
        return jsonify({"error": "Formato inválido. Necessário o parâmetro Header = Content-Type: application/json."}), 400
    
    dados_usuario = request.json

    if len(dados_usuario) not in (3,4) :
        return jsonify({"error": "Formato de payload inválido. Necessário 3 campos no payload (NM_USUARIO, CPF, ID_FUNCAO, *SENHA). A senha é facultativa."}), 400
    
    if not dados_usuario.get('NM_USUARIO') or not dados_usuario.get('CPF') or not dados_usuario.get('ID_FUNCAO'):
        list = [x for x in ('NM_USUARIO','CPF','ID_FUNCAO') if x not in dados_usuario]

        return jsonify({"error": "Formato de payload inválido. Campos faltantes: {}".format(list)}), 400

    dados_usuario['ALTERED_AT'] = datetime.now()
    dados_usuario['SENHA'] = handler_password.gerar_hash(str(dados_usuario['SENHA']).encode('utf-8')).decode('utf-8') if dados_usuario.get('SENHA') else None
    dados_usuario['ID'] = id

    with db_connection_handler as db:
        try:
            db.begin() if not db.in_transaction() else None
            result = db.execute(repository_usuario.alter_user(dados_usuario))
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
            return {'Error': 'Houve um erro no banco de dados.'}, 400
    
    if result.rowcount == 0:
        return jsonify({'error': 'ID_USUARIO não encontrado.', 'dados': dados_usuario}), 404
    else:
        return jsonify({'message': 'Usuário alterado com sucesso!', 'dados': dados_usuario}), 200

@app.route('/usuarios/delete/<id>', methods=['POST'])
def deletar_usuario(id):
    with db_connection_handler as db:
        try:
            db.begin() if not db.in_transaction() else None
            result = db.execute(repository_usuario.delete_user(id))
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
            return {'Error': 'Houve um erro no banco de dados.'}, 400
    
    if result.rowcount == 0:
        return jsonify({'error': f'ID_USUARIO {id} não encontrado.'}), 404
    else:
        return jsonify({'message': 'Usuário deletado com sucesso!'}), 200

###### FUNCOES ######
@app.route('/funcoes', methods=['GET'])
def funcoes():
    response = None
    with db_connection_handler as db:
        response = db.execute(repository_funcao.select_all()).fetchall()
        response_dict = [{'Função': j[1], 'Nível Acesso': j[2]}  for i,j in enumerate(response)]
    return jsonify(response_dict), 200

###### SALAS ######
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
        try:
            db.begin() if not db.in_transaction() else None
            db.execute(repository_sala.insert_room(dados_sala))
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
            return {'Error': 'Houve um erro no banco de dados.'}, 400
        
        
    return jsonify({'message': 'Sala cadastrada com sucesso!', 'dados': dados_sala}), 200

@app.route('/salas/alter/<id>', methods=['POST'])
def alterar_sala(id):
    if not request.is_json:
        return jsonify({"error": "Formato inválido. Necessário o parâmetro Header = Content-Type: application/json."}), 400
    
    dados_sala = request.json

    if len(dados_sala) != 2:
        return jsonify({"error": "Formato de payload inválido. Necessário 2 campos no payload (DE_SALA, NVL_ACESSO)."}), 400
    
    if not dados_sala.get('DE_SALA') or not dados_sala.get('NVL_ACESSO') :
        list = [x for x in ('DE_SALA','NVL_ACESSO') if x not in dados_sala]

        return jsonify({"error": "Formato de payload inválido. Campos faltantes: {}".format(list)}), 400

    dados_sala['ALTERED_AT'] = datetime.now()
    dados_sala['ID'] = id

    with db_connection_handler as db:
        try:
            db.begin() if not db.in_transaction() else None
            result = db.execute(repository_sala.alter_room(dados_sala))
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
            return {'Error': 'Houve um erro no banco de dados.'}, 400
    
    if result.rowcount == 0:
        return jsonify({'error': 'ID_SALA não encontrado.'}), 404
    else:
        return jsonify({'message': 'Sala alterada com sucesso!', 'dados': dados_sala}), 200

@app.route('/salas/delete/<id>', methods=['POST'])
def deletar_sala(id):
    with db_connection_handler as db:
        try:
            db.begin() if not db.in_transaction() else None
            result = db.execute(repository_sala.delete_room(id))
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
            return {'Error': 'Houve um erro no banco de dados.'}, 400
    
    if result.rowcount == 0:
        return jsonify({'error': f'ID_SALA {id} não encontrado.'}), 404
    else:
        return jsonify({'message': 'Sala deletada com sucesso!'}), 200

###### INVENTÁRIO ######
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
        
    return jsonify({'message': 'Recurso cadastrado com sucesso!', 'dados': dados_item}), 200

@app.route('/inventario/alter/<id>', methods=['POST'])
def alterar_item(id):
    if not request.is_json:
        return jsonify({"error": "Formato inválido. Necessário o parâmetro Header = Content-Type: application/json."}), 400
    
    dados_item = request.json

    if len(dados_item) != 3:
        return jsonify({"error": "Formato de payload inválido. Necessário 3 campos no payload (DE_RECURSO,NR_SERIE,ID_SALA)."}), 400
    
    if not dados_item.get('DE_RECURSO') or not dados_item.get('NR_SERIE') or not dados_item.get('ID_SALA') :
        list = [x for x in ('DE_RECURSO','NR_SERIE','ID_SALA') if x not in dados_item]
        return jsonify({"error": "Formato de payload inválido. Campos faltantes: {}".format(list)}), 400

    dados_item['ALTERED_AT'] = datetime.now()
    dados_item['ID'] = id

    with db_connection_handler as db:
        try:
            db.begin() if not db.in_transaction() else None
            result = db.execute(repository_inventory.alter_item(dados_item))
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
            return {'Error': 'Houve um erro no banco de dados.'}, 400
    
    if result.rowcount == 0:
        return jsonify({'error': 'ID_RECURSO não encontrado.'}), 404
    else:
        return jsonify({'message': 'Recurso alterado com sucesso!', 'dados': dados_item}), 200

@app.route('/inventario/delete/<id>', methods=['POST'])
def deletar_item(id):
    with db_connection_handler as db:
        try:
            db.begin() if not db.in_transaction() else None
            result = db.execute(repository_inventory.delete_item(id))
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
            return {'Error': 'Houve um erro no banco de dados.'}, 400
    
    if result.rowcount == 0:
        return jsonify({'error': f'ID_RECURSO {id} não encontrado.'}), 404
    else:
        return jsonify({'message': 'Recurso deletado com sucesso!'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
