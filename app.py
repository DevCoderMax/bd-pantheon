from flask import Flask, jsonify
import mysql.connector
from mysql.connector import Error
import requests

app = Flask(__name__)

# Configurações do banco de dados
DB_CONFIG = {
    'host': 'dbserver.dev.f92a9e36-50c7-46cb-99f1-c31cb3846d61.drush.in',
    'user': 'pantheon',
    'password': 'iCNgNhkrX0H1jF8g9M2THkaXIOPe2QzR',
    'database': 'pantheon',
    'port': 12816
}

# URL para ativar o sandbox
SANDBOX_URL = 'https://dev-max-eternal.pantheonsite.io/'

@app.route('/ativar-sandbox', methods=['GET'])  # Alterado de 'POST' para 'GET'
def ativar_sandbox():
    try:
        # Tenta conectar ao banco de dados
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            db_info = cursor.fetchone()
            return jsonify({
                'status': 'Conexão com o banco de dados estabelecida',
                'database': db_info[0]
            }), 200
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        # Se falhar, envia requisição para ativar o sandbox
        try:
            response = requests.post(SANDBOX_URL)
            if response.status_code == 200:
                return jsonify({
                    'status': 'Sandbox ativado com sucesso',
                    'url': SANDBOX_URL
                }), 200
            else:
                return jsonify({
                    'status': 'Falha ao ativar o sandbox',
                    'response_code': response.status_code
                }), 500
        except requests.RequestException as req_e:
            print(f"Erro ao enviar requisição para o sandbox: {req_e}")
            return jsonify({
                'status': 'Erro ao tentar ativar o sandbox',
                'error': str(req_e)
            }), 500
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()


@app.route('/listar-tabelas', methods=['GET'])
def listar_tabelas():
    try:
        # Tenta conectar ao banco de dados
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Executa a consulta para listar todas as tabelas
            cursor.execute("SHOW TABLES;")
            tabelas = cursor.fetchall()
            
            # Formata o resultado
            lista_tabelas = [tabela[0] for tabela in tabelas]
            
            return jsonify({
                'status': 'Sucesso',
                'tabelas': lista_tabelas
            }), 200
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return jsonify({
            'status': 'Erro',
            'mensagem': 'Falha ao listar tabelas do banco de dados',
            'erro': str(e)
        }), 500
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()


@app.route('/limpar-banco', methods=['POST'])
def limpar_banco():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Desativa as verificações de chave estrangeira temporariamente
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            
            # Lista todas as tabelas
            cursor.execute("SHOW TABLES;")
            tabelas = cursor.fetchall()
            
            # Exclui todas as tabelas
            for tabela in tabelas:
                cursor.execute(f"DROP TABLE IF EXISTS `{tabela[0]}`;")
            
            # Reativa as verificações de chave estrangeira
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            
            connection.commit()
            
            return jsonify({
                'status': 'Sucesso',
                'mensagem': 'Todas as tabelas foram removidas do banco de dados'
            }), 200
    except Error as e:
        print(f"Erro ao limpar o banco de dados: {e}")
        return jsonify({
            'status': 'Erro',
            'mensagem': 'Falha ao limpar o banco de dados',
            'erro': str(e)
        }), 500
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()


@app.route('/info-tabela/<nome_tabela>', methods=['GET'])
def info_tabela(nome_tabela):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Verifica se a tabela existe
            cursor.execute(f"SHOW TABLES LIKE '{nome_tabela}'")
            if not cursor.fetchone():
                return jsonify({
                    'status': 'Erro',
                    'mensagem': f'A tabela {nome_tabela} não existe'
                }), 404
            
            # Obtém informações sobre as colunas da tabela
            cursor.execute(f"DESCRIBE {nome_tabela}")
            colunas = cursor.fetchall()
            
            # Obtém uma amostra dos dados da tabela
            cursor.execute(f"SELECT * FROM {nome_tabela} LIMIT 5")
            amostra_dados = cursor.fetchall()
            
            return jsonify({
                'status': 'Sucesso',
                'nome_tabela': nome_tabela,
                'colunas': colunas,
                'amostra_dados': amostra_dados
            }), 200
    except Error as e:
        print(f"Erro ao obter informações da tabela: {e}")
        return jsonify({
            'status': 'Erro',
            'mensagem': 'Falha ao obter informações da tabela',
            'erro': str(e)
        }), 500
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)