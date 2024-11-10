from quart import Quart, jsonify , request, Response
import asyncmy
import aiohttp
import asyncio
from asyncmy.cursors import DictCursor  # Importação adicionada
from functools import wraps

app = Quart(__name__)

# Configurações do banco de dados
DB_CONFIG = {
    'host': 'dbserver.dev.f92a9e36-50c7-46cb-99f1-c31cb3846d61.drush.in',
    'user': 'pantheon',
    'password': 'iCNgNhkrX0H1jF8g9M2THkaXIOPe2QzR',
    'db': 'pantheon',
    'port': 12816,
    'autocommit': True
}

# URL para ativar o sandbox caso a conexão com o banco de dados falhar
SANDBOX_URL = 'https://dev-max-eternal.pantheonsite.io/'

# Pool de conexões
pool = None

async def init_db_pool():
    """
    Inicializa o pool de conexoes com o banco de dados.

    O pool   criado com o tamanho maximo de 10 conexoes e o tamanho maximo de 10 conexoes.
    """
    global pool
    pool = await asyncmy.create_pool(**DB_CONFIG, maxsize=10)

@app.before_serving
async def startup():
    """
    Inicializa o pool de conexoes com o banco de dados antes de
    o servidor de API ser iniciado.

    Esta fun o   chamada automaticamente pelo Quart antes de
    o servidor ser iniciado.
    """
    await init_db_pool()

async def tentar_reconexao():
    """Tenta reconectar ao banco de dados através do sandbox"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(SANDBOX_URL) as response:
                if response.status != 200:
                    raise Exception(f"Falha ao ativar o sandbox. Status code: {response.status}")
            await init_db_pool()
            return True
        except Exception as e:
            print(f"Erro na reconexão: {e}")
            return False

def cors_response(response):
    """Adiciona headers CORS à resposta"""
    if not isinstance(response, Response):
        response = Response(response)
    
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Max-Age'] = '86400'  # 24 horas
    return response

def tratamento_conexao():
    """Decorator para tratar erros de conexão com o banco de dados"""
    def decorator(func):
        @wraps(func)  # Preserva os metadados da função original
        async def wrapper(*args, **kwargs):
            try:
                response = await func(*args, **kwargs)
                return cors_response(response)  # Aplica CORS na resposta
            except (asyncmy.Error, AttributeError) as e:
                print(f"Erro de conexão: {e}")
                if await tentar_reconexao():
                    try:
                        response = await func(*args, **kwargs)
                        return cors_response(response)  # Aplica CORS na resposta
                    except Exception as e:
                        erro = jsonify({
                            'status': 'Erro',
                            'mensagem': f'Falha após tentativa de reconexão: {str(e)}'
                        }), 500
                        return cors_response(erro)
                else:
                    erro = jsonify({
                        'status': 'Erro',
                        'mensagem': 'Não foi possível reconectar ao banco de dados'
                    }), 500
                    return cors_response(erro)
        return wrapper
    return decorator

@app.route('/ativar-sandbox', methods=['GET'])
async def ativar_sandbox():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(SANDBOX_URL) as response:
                if response.status != 200:
                    raise Exception(f"Falha ao ativar o sandbox. Status code: {response.status}")
            
            async with pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute("SELECT DATABASE();")
                    db_info = await cursor.fetchone()
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

@app.route('/listar-tabelas', methods=['GET'])
@tratamento_conexao()
async def listar_tabelas():
    try:
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SHOW TABLES;")
                tabelas = await cursor.fetchall()
                lista_tabelas = [tabela[0] for tabela in tabelas]
                return jsonify({
                    'status': 'Sucesso',
                    'tabelas': lista_tabelas
                }), 200
    except Exception as e:
        print(f"Erro ao listar tabelas: {e}")
        return jsonify({
            'status': 'Erro',
            'mensagem': 'Falha ao listar tabelas do banco de dados',
            'erro': str(e)
        }), 500

@app.route('/limpar-banco', methods=['POST'])
@tratamento_conexao()
async def limpar_banco():
    try:
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
                await cursor.execute("SHOW TABLES;")
                tabelas = await cursor.fetchall()
                drop_queries = [f"DROP TABLE IF EXISTS `{tabela[0]}`;" for tabela in tabelas]
                await cursor.execute("; ".join(drop_queries))
                await cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            await connection.commit()
            return jsonify({
                'status': 'Sucesso',
                'mensagem': 'Todas as tabelas foram removidas do banco de dados'
            }), 200
    except Exception as e:
        print(f"Erro ao limpar banco: {e}")
        return jsonify({
            'status': 'Erro',
            'mensagem': 'Falha ao limpar o banco de dados',
            'erro': str(e)
        }), 500

@app.route('/info-tabela/<nome_tabela>', methods=['GET'])
@tratamento_conexao()
async def info_tabela(nome_tabela):
    try:
        async with pool.acquire() as connection:
            async with connection.cursor(DictCursor) as cursor:
                await cursor.execute(f"SHOW TABLES LIKE '{nome_tabela}'")
                if not await cursor.fetchone():
                    return jsonify({
                        'status': 'Erro',
                        'mensagem': f'A tabela {nome_tabela} não existe'
                    }), 404

                await cursor.execute(f"DESCRIBE {nome_tabela}")
                colunas = await cursor.fetchall()
                
                await cursor.execute(f"SELECT * FROM {nome_tabela} LIMIT 5")
                amostra_dados = await cursor.fetchall()
                
                return jsonify({
                    'status': 'Sucesso',
                    'nome_tabela': nome_tabela,
                    'colunas': colunas,
                    'amostra_dados': amostra_dados
                }), 200
    except Exception as e:
        print(f"Erro ao obter informações da tabela: {e}")
        return jsonify({
            'status': 'Erro',
            'mensagem': 'Falha ao obter informações da tabela',
            'erro': str(e)
        }), 500

@app.route('/limpar-tabela/<nome_tabela>', methods=['POST'])
@tratamento_conexao()
async def limpar_tabela(nome_tabela):
    try:
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                # Verifica se a tabela existe
                await cursor.execute(f"SHOW TABLES LIKE '{nome_tabela}'")
                if not await cursor.fetchone():
                    return jsonify({
                        'status': 'Erro',
                        'mensagem': f'A tabela {nome_tabela} não existe'
                    }), 404

                # Limpa os dados da tabela
                await cursor.execute(f"TRUNCATE TABLE `{nome_tabela}`")
            await connection.commit()
            return jsonify({
                'status': 'Sucesso',
                'mensagem': f'Todos os dados da tabela {nome_tabela} foram removidos'
            }), 200
    except Exception as e:
        print(f"Erro ao limpar tabela {nome_tabela}: {e}")
        return jsonify({
            'status': 'Erro',
            'mensagem': f'Falha ao limpar os dados da tabela {nome_tabela}',
            'erro': str(e)
        }), 500

@app.route('/criar-tabela', methods=['POST'])
@tratamento_conexao()
async def criar_tabela():
    try:
        dados = await request.get_json()
        nome_tabela = dados.get('nome_tabela')
        colunas = dados.get('colunas')

        if not nome_tabela or not colunas:
            return jsonify({
                'status': 'Erro',
                'mensagem': 'Nome da tabela e definição das colunas são obrigatórios'
            }), 400

        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                # Verifica se a tabela já existe
                await cursor.execute(f"SHOW TABLES LIKE '{nome_tabela}'")
                if await cursor.fetchone():
                    return jsonify({
                        'status': 'Erro',
                        'mensagem': f'A tabela {nome_tabela} já existe'
                    }), 409

                # Cria a query SQL para criar a tabela
                colunas_sql = ', '.join([f"{coluna['nome']} {coluna['tipo']}" for coluna in colunas])
                query = f"CREATE TABLE `{nome_tabela}` ({colunas_sql})"

                # Executa a query para criar a tabela
                await cursor.execute(query)
            await connection.commit()

        return jsonify({
            'status': 'Sucesso',
            'mensagem': f'Tabela {nome_tabela} criada com sucesso'
        }), 201
    except Exception as e:
        print(f"Erro ao criar tabela: {e}")
        return jsonify({
            'status': 'Erro',
            'mensagem': 'Falha ao criar a tabela',
            'erro': str(e)
        }), 500

#executar comando sql e retornar o resultado
@app.route('/executar-sql', methods=['POST'])
@tratamento_conexao()
async def executar_sql():
    dados = await request.get_json()
    comando = dados.get('comando')

    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(comando)
            resultado = await cursor.fetchall()
            return jsonify({
                'status': 'Sucesso',
                'resultado': resultado
            }), 200

# apagar tabela
@app.route('/apagar-tabela/<nome_tabela>', methods=['GET'])
@tratamento_conexao()
async def apagar_tabela(nome_tabela):
    try:
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"DROP TABLE IF EXISTS `{nome_tabela}`")
                await connection.commit()
                return jsonify({
                    'status': 'Sucesso',
                    'mensagem': f'Tabela {nome_tabela} apagada com sucesso'
                }), 200
    except Exception as e:
        print(f"Erro ao apagar tabela {nome_tabela}: {e}")
        return jsonify({
            'status': 'Erro',
            'mensagem': f'Falha ao apagar a tabela {nome_tabela}',
            'erro': str(e)
        }), 500

# Adicione uma rota específica para OPTIONS
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
async def handle_options(path):
    response = Response('')
    return cors_response(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)