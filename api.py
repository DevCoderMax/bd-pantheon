from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
import requests
import time
from info_bd import host, user, password, database, port
import ngrok
import asyncio
import up_links

app = Flask(__name__)

def activate_sandbox():
    try:
        response = requests.get("https://dev-max-eternal.pantheonsite.io/")
        if response.status_code == 200:
            print("Sandbox ativado com sucesso.")
        else:
            print(f"Falha ao ativar o sandbox. Código de status: {response.status_code}")
    except requests.RequestException as e:
        print(f"Erro ao fazer a requisição para ativar o sandbox: {e}")

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        if connection.is_connected():
            print("Conexão estabelecida com sucesso.")
            db_info = connection.get_server_info()
            print("Versão do MySQL:", db_info)
            return connection
    except Error as e:
        print("Erro ao conectar ao MySQL:", e)
        return None

def execute_sql_command(command):
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute(command)
            result = cursor.fetchall()  # Obtém todos os resultados
            connection.commit()  # Confirma a transação, se necessário
            return result
        except Error as e:
            print("Erro ao executar o comando SQL:", e)
            return None
        finally:
            cursor.close()
            connection.close()
    return None

def list_tables():
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SHOW TABLES;")  # Comando para listar tabelas
            tables = cursor.fetchall()  # Obtém todas as tabelas
            return [table[0] for table in tables]  # Retorna uma lista de nomes de tabelas
        except Error as e:
            print("Erro ao listar tabelas:", e)
            return None
        finally:
            cursor.close()
            connection.close()
    return None

def drop_all_tables():
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SHOW TABLES;")  # Obtém todas as tabelas
            tables = cursor.fetchall()
            for table in tables:
                cursor.execute(f"DROP TABLE {table[0]};")  # Apaga cada tabela
            connection.commit()  # Confirma a transação
            return True
        except Error as e:
            print("Erro ao apagar tabelas:", e)
            return False
        finally:
            cursor.close()
            connection.close()
    return False

def list_table_data(table_name):
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute(f"SELECT * FROM {table_name};")  # Comando para listar todos os dados da tabela
            data = cursor.fetchall()  # Obtém todos os dados
            columns = [desc[0] for desc in cursor.description]  # Obtém os nomes das colunas
            return {"columns": columns, "data": data}
        except Error as e:
            print(f"Erro ao listar dados da tabela {table_name}:", e)
            return None
        finally:
            cursor.close()
            connection.close()
    return None

async def setup_ngrok():
    listener = await ngrok.connect(5000, authtoken="2bYKV64FlaHhbSUWb5EryBGpMCc_3vbjLhByLR4VZNGFzwKMF")
    print(f"Ingress estabelecido em: {listener.url()}")
    up_links.salvar_conteudo(listener.url())

@app.route('/activate_sandbox', methods=['GET'])
def api_activate_sandbox():
    activate_sandbox()
    return jsonify({"message": "Sandbox ativado."}), 200

@app.route('/connect', methods=['GET'])
def api_connect():
    start_time = time.time()
    connection = None

    while time.time() - start_time < 3:  # Tentativa de conexão durante  minuto
        connection = connect_to_database()
        if connection:
            break
        time.sleep(5)

    if not connection:
        return jsonify({"message": "Falha ao conectar ao banco de dados dentro de 1 minuto."}), 500
    else:
        connection.close()
        return jsonify({"message": "Conexão estabelecida e encerrada."}), 200

@app.route('/execute_sql', methods=['POST'])
def api_execute_sql():
    command = request.json.get('command')  # Obtém o comando SQL do corpo da requisição
    result = execute_sql_command(command)
    if result is not None:
        return jsonify({"result": result}), 200
    else:
        return jsonify({"message": "Erro ao executar o comando SQL."}), 500

@app.route('/tables', methods=['GET'])
def api_list_tables():
    tables = list_tables()
    if tables is not None:
        return jsonify({"tables": tables}), 200
    else:
        return jsonify({"message": "Erro ao listar tabelas."}), 500

@app.route('/drop_all_tables', methods=['DELETE'])
def api_drop_all_tables():
    if drop_all_tables():
        return jsonify({"message": "Todas as tabelas foram apagadas com sucesso."}), 200
    else:
        return jsonify({"message": "Erro ao apagar as tabelas."}), 500

@app.route('/table_data/<table_name>', methods=['GET'])
def api_list_table_data(table_name):
    table_data = list_table_data(table_name)
    if table_data is not None:
        return jsonify(table_data), 200
    else:
        return jsonify({"message": f"Erro ao listar dados da tabela {table_name}."}), 500

if __name__ == "__main__":
    asyncio.run(setup_ngrok())  # Inicia o ngrok antes de iniciar o servidor Flask
    app.run(debug=True, use_reloader=False)  # Desativa o reloader para evitar duplicação

@app.before_first_request
def initialize_ngrok():
    asyncio.run(setup_ngrok())