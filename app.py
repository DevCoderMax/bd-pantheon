from flask import Flask, jsonify
import mysql.connector
from mysql.connector import Error
import requests
import time

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

def tentar_conexao(max_tentativas=3):
    for tentativa in range(max_tentativas):
        try:
            # Primeiro, tenta ativar o sandbox
            response = requests.post(SANDBOX_URL)
            if response.status_code != 200:
                raise Exception(f"Falha ao ativar o sandbox. Status code: {response.status_code}")
            
            # Se o sandbox foi ativado com sucesso, tenta a conexão com o banco de dados
            connection = mysql.connector.connect(**DB_CONFIG)
            if connection.is_connected():
                return connection
        except (Error, requests.RequestException) as e:
            print(f"Tentativa {tentativa + 1} falhou: {e}")
            if tentativa < max_tentativas - 1:
                time.sleep(2)  # Espera 2 segundos antes da próxima tentativa
    
    raise Exception("Falha ao conectar após várias tentativas")

@app.route('/ativar-sandbox', methods=['GET'])
def ativar_sandbox():
    try:
        connection = tentar_conexao()
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        db_info = cursor.fetchone()
        return jsonify({
            'status': 'Conexão com o banco de dados estabelecida',
            'database': db_info[0]
        }), 200
    except Exception as e:
        print(f"Erro ao ativar sandbox: {e}")
        return jsonify({
            'status': 'Erro',
            'mensagem': 'Falha ao ativar o sandbox e conectar ao banco de dados',
            'erro': str(e)
        }), 500
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def executar_com_tentativas(funcao, max_tentativas=2):
    for tentativa in range(max_tentativas):
        try:
            return funcao()
        except Exception as e:
            print(f"Tentativa {tentativa + 1} falhou: {e}")
            if tentativa == max_tentativas - 1:
                raise
            time.sleep(2)  # Espera 2 segundos antes da próxima tentativa

@app.route('/listar-tabelas', methods=['GET'])
def listar_tabelas():
    def _listar_tabelas():
        connection = tentar_conexao()
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES;")
        tabelas = cursor.fetchall()
        lista_tabelas = [tabela[0] for tabela in tabelas]
        cursor.close()
        connection.close()
        return jsonify({
            'status': 'Sucesso',
            'tabelas': lista_tabelas
        }), 200

    try:
        return executar_com_tentativas(_listar_tabelas)
    except Exception as e:
        return jsonify({
            'status': 'Erro',
            'mensagem': 'Falha ao listar tabelas do banco de dados',
            'erro': str(e)
        }), 500

@app.route('/limpar-banco', methods=['POST'])
def limpar_banco():
    def _limpar_banco():
        connection = tentar_conexao()
        cursor = connection.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("SHOW TABLES;")
        tabelas = cursor.fetchall()
        for tabela in tabelas:
            cursor.execute(f"DROP TABLE IF EXISTS `{tabela[0]}`;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({
            'status': 'Sucesso',
            'mensagem': 'Todas as tabelas foram removidas do banco de dados'
        }), 200

    try:
        return executar_com_tentativas(_limpar_banco)
    except Exception as e:
        return jsonify({
            'status': 'Erro',
            'mensagem': 'Falha ao limpar o banco de dados',
            'erro': str(e)
        }), 500

@app.route('/info-tabela/<nome_tabela>', methods=['GET'])
def info_tabela(nome_tabela):
    def _info_tabela():
        connection = tentar_conexao()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"SHOW TABLES LIKE '{nome_tabela}'")
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'Erro',
                'mensagem': f'A tabela {nome_tabela} não existe'
            }), 404
        cursor.execute(f"DESCRIBE {nome_tabela}")
        colunas = cursor.fetchall()
        cursor.execute(f"SELECT * FROM {nome_tabela} LIMIT 5")
        amostra_dados = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify({
            'status': 'Sucesso',
            'nome_tabela': nome_tabela,
            'colunas': colunas,
            'amostra_dados': amostra_dados
        }), 200

    try:
        return executar_com_tentativas(_info_tabela)
    except Exception as e:
        return jsonify({
            'status': 'Erro',
            'mensagem': 'Falha ao obter informações da tabela',
            'erro': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)