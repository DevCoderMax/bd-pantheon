import mysql.connector
from mysql.connector import Error
import requests
import time
from flask import Flask, jsonify  # Importando Flask e jsonify

app = Flask(__name__)  # Inicializando a aplicação Flask

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
            host='dbserver.dev.f92a9e36-50c7-46cb-99f1-c31cb3846d61.drush.in',
            user='pantheon',
            password='iCNgNhkrX0H1jF8g9M2THkaXIOPe2QzR',
            database='pantheon',
            port=12816
        )
        if connection.is_connected():
            print("Conexão estabelecida com sucesso.")
            db_info = connection.get_server_info()
            print("Versão do MySQL:", db_info)
            return connection
    except Error as e:
        print("Erro ao conectar ao MySQL:", e)
        return None

def get_tables(connection):
    """Função para obter todas as tabelas do banco de dados."""
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        return [table[0] for table in tables]  # Retorna uma lista de nomes de tabelas
    except Error as e:
        print("Erro ao obter tabelas:", e)
        return []

@app.route('/tables', methods=['GET'])  # Rota para visualizar tabelas
def tables_route():
    connection = connect_to_database()
    if connection:
        tables = get_tables(connection)
        connection.close()
        return jsonify(tables)  # Retorna as tabelas em formato JSON
    else:
        return jsonify({"error": "Falha ao conectar ao banco de dados."}), 500

def drop_all_tables(connection):
    """Função para excluir todas as tabelas do banco de dados."""
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        for table in tables:
            cursor.execute(f"DROP TABLE {table[0]};")  # Exclui cada tabela
        connection.commit()  # Confirma as alterações
        return {"message": "Todas as tabelas foram excluídas com sucesso."}
    except Error as e:
        print("Erro ao excluir tabelas:", e)
        return {"error": str(e)}

@app.route('/drop_tables', methods=['DELETE'])  # Rota para excluir todas as tabelas
def drop_tables_route():
    connection = connect_to_database()
    if connection:
        result = drop_all_tables(connection)
        connection.close()
        return jsonify(result)  # Retorna o resultado em formato JSON
    else:
        return jsonify({"error": "Falha ao conectar ao banco de dados."}), 500

def main():
    activate_sandbox()
    start_time = time.time()
    connection = None

    while time.time() - start_time < 60:  # Tentativa de conexão durante 1 minuto
        connection = connect_to_database()
        if connection:
            break  # Conexão bem-sucedida, sai do loop
        time.sleep(5)  # Aguarda 5 segundos antes da próxima tentativa

    if not connection:
        print("Falha ao conectar ao banco de dados dentro de 1 minuto.")
    else:
        print("Conexão estabelecida e pronto para uso.")
        # Aqui você pode prosseguir com as operações no banco de dados

        # Lembre-se de fechar a conexão após o uso
        connection.close()
        print("Conexão ao MySQL foi encerrada.")

if __name__ == "__main__":
    app.run(debug=True)  # Inicia a aplicação Flask
    main()  # Chama a função main para executar o restante do código
