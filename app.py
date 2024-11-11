from fastapi import FastAPI, Response, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncmy
import requests
from asyncmy.cursors import DictCursor
from functools import wraps
from typing import Optional, Dict, List, Any
from pydantic import BaseModel

app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurações do banco de dados
DB_CONFIG = {
    'host': 'dbserver.dev.f92a9e36-50c7-46cb-99f1-c31cb3846d61.drush.in',
    'user': 'pantheon',
    'password': 'iCNgNhkrX0H1jF8g9M2THkaXIOPe2QzR',
    'db': 'pantheon',
    'port': 12816,
    'autocommit': True
}

# URL para ativar o sandbox
SANDBOX_URL = 'https://dev-max-eternal.pantheonsite.io/'

# Pool de conexões
pool = None

# Models para validação de dados
class Coluna(BaseModel):
    nome: str
    tipo: str

class CriarTabelaRequest(BaseModel):
    nome_tabela: str
    colunas: List[Coluna]

class ComandoSQLRequest(BaseModel):
    comando: str

async def init_db_pool():
    """Inicializa o pool de conexões com o banco de dados."""
    global pool
    pool = await asyncmy.create_pool(**DB_CONFIG, maxsize=10)

async def tentar_reconexao():
    """Tenta reconectar ao banco de dados através do sandbox"""
    try:
        response = requests.get(SANDBOX_URL)
        if response.status_code != 200:
            raise Exception(f"Falha ao ativar o sandbox. Status code: {response.status_code}")
        await init_db_pool()
        return True
    except Exception as e:
        print(f"Erro na reconexão: {e}")
        return False

def tratamento_conexao():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                response = await func(*args, **kwargs)
                return response
            except (asyncmy.Error, AttributeError) as e:
                print(f"Erro de conexão: {e}")
                if await tentar_reconexao():
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        return JSONResponse(
                            status_code=500,
                            content={
                                'status': 'Erro',
                                'mensagem': f'Falha após tentativa de reconexão: {str(e)}'
                            }
                        )
                else:
                    return JSONResponse(
                        status_code=500,
                        content={
                            'status': 'Erro',
                            'mensagem': 'Não foi possível reconectar ao banco de dados'
                        }
                    )
        return wrapper
    return decorator

@app.on_event("startup")
async def startup_event():
    await init_db_pool()

@app.get("/ativar-sandbox")
async def ativar_sandbox():
    try:
        response = requests.get(SANDBOX_URL)
        if response.status_code != 200:
            raise Exception(f"Falha ao ativar o sandbox. Status code: {response.status_code}")
        
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT DATABASE();")
                db_info = await cursor.fetchone()
                return JSONResponse(
                    status_code=200,
                    content={
                        'status': 'Conexão com o banco de dados estabelecida',
                        'database': db_info[0]
                    }
                )
    except Exception as e:
        print(f"Erro ao ativar sandbox: {e}")
        return JSONResponse(
            status_code=500,
            content={
                'status': 'Erro',
                'mensagem': 'Falha ao ativar o sandbox e conectar ao banco de dados',
                'erro': str(e)
            }
        )

@app.get("/listar-tabelas")
@tratamento_conexao()
async def listar_tabelas():
    try:
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SHOW TABLES;")
                tabelas = await cursor.fetchall()
                lista_tabelas = [tabela[0] for tabela in tabelas]
                return JSONResponse(
                    status_code=200,
                    content={
                        'status': 'Sucesso',
                        'tabelas': lista_tabelas
                    }
                )
    except Exception as e:
        print(f"Erro ao listar tabelas: {e}")
        return JSONResponse(
            status_code=500,
            content={
                'status': 'Erro',
                'mensagem': 'Falha ao listar tabelas do banco de dados',
                'erro': str(e)
            }
        )

@app.post("/limpar-banco")
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
            return JSONResponse(
                status_code=200,
                content={
                    'status': 'Sucesso',
                    'mensagem': 'Todas as tabelas foram removidas do banco de dados'
                }
            )
    except Exception as e:
        print(f"Erro ao limpar banco: {e}")
        return JSONResponse(
            status_code=500,
            content={
                'status': 'Erro',
                'mensagem': 'Falha ao limpar o banco de dados',
                'erro': str(e)
            }
        )

@app.get("/info-tabela/{nome_tabela}")
@tratamento_conexao()
async def info_tabela(nome_tabela: str):
    try:
        async with pool.acquire() as connection:
            async with connection.cursor(DictCursor) as cursor:
                await cursor.execute(f"SHOW TABLES LIKE '{nome_tabela}'")
                if not await cursor.fetchone():
                    return JSONResponse(
                        status_code=404,
                        content={
                            'status': 'Erro',
                            'mensagem': f'A tabela {nome_tabela} não existe'
                        }
                    )

                await cursor.execute(f"DESCRIBE {nome_tabela}")
                colunas = await cursor.fetchall()
                
                await cursor.execute(f"SELECT * FROM {nome_tabela} LIMIT 5")
                amostra_dados = await cursor.fetchall()
                
                return JSONResponse(
                    status_code=200,
                    content={
                        'status': 'Sucesso',
                        'nome_tabela': nome_tabela,
                        'colunas': colunas,
                        'amostra_dados': amostra_dados
                    }
                )
    except Exception as e:
        print(f"Erro ao obter informações da tabela: {e}")
        return JSONResponse(
            status_code=500,
            content={
                'status': 'Erro',
                'mensagem': 'Falha ao obter informações da tabela',
                'erro': str(e)
            }
        )

@app.post("/limpar-tabela/{nome_tabela}")
@tratamento_conexao()
async def limpar_tabela(nome_tabela: str):
    try:
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"SHOW TABLES LIKE '{nome_tabela}'")
                if not await cursor.fetchone():
                    return JSONResponse(
                        status_code=404,
                        content={
                            'status': 'Erro',
                            'mensagem': f'A tabela {nome_tabela} não existe'
                        }
                    )

                await cursor.execute(f"TRUNCATE TABLE `{nome_tabela}`")
            await connection.commit()
            return JSONResponse(
                status_code=200,
                content={
                    'status': 'Sucesso',
                    'mensagem': f'Todos os dados da tabela {nome_tabela} foram removidos'
                }
            )
    except Exception as e:
        print(f"Erro ao limpar tabela {nome_tabela}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                'status': 'Erro',
                'mensagem': f'Falha ao limpar os dados da tabela {nome_tabela}',
                'erro': str(e)
            }
        )

@app.post("/criar-tabela")
@tratamento_conexao()
async def criar_tabela(request: CriarTabelaRequest):
    try:
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"SHOW TABLES LIKE '{request.nome_tabela}'")
                if await cursor.fetchone():
                    return JSONResponse(
                        status_code=409,
                        content={
                            'status': 'Erro',
                            'mensagem': f'A tabela {request.nome_tabela} já existe'
                        }
                    )

                colunas_sql = ', '.join([f"{coluna.nome} {coluna.tipo}" for coluna in request.colunas])
                query = f"CREATE TABLE `{request.nome_tabela}` ({colunas_sql})"
                await cursor.execute(query)
            await connection.commit()

        return JSONResponse(
            status_code=201,
            content={
                'status': 'Sucesso',
                'mensagem': f'Tabela {request.nome_tabela} criada com sucesso'
            }
        )
    except Exception as e:
        print(f"Erro ao criar tabela: {e}")
        return JSONResponse(
            status_code=500,
            content={
                'status': 'Erro',
                'mensagem': 'Falha ao criar a tabela',
                'erro': str(e)
            }
        )

@app.post("/executar-sql")
@tratamento_conexao()
async def executar_sql(request: ComandoSQLRequest):
    try:
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(request.comando)
                resultado = await cursor.fetchall()
                return JSONResponse(
                    status_code=200,
                    content={
                        'status': 'Sucesso',
                        'resultado': resultado
                    }
                )
    except Exception as e:
        print(f"Erro ao executar SQL: {e}")
        return JSONResponse(
            status_code=500,
            content={
                'status': 'Erro',
                'mensagem': 'Falha ao executar comando SQL',
                'erro': str(e)
            }
        )

@app.get("/apagar-tabela/{nome_tabela}")
@tratamento_conexao()
async def apagar_tabela(nome_tabela: str):
    try:
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(f"DROP TABLE IF EXISTS `{nome_tabela}`")
                await connection.commit()
                return JSONResponse(
                    status_code=200,
                    content={
                        'status': 'Sucesso',
                        'mensagem': f'Tabela {nome_tabela} apagada com sucesso'
                    }
                )
    except Exception as e:
        print(f"Erro ao apagar tabela {nome_tabela}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                'status': 'Erro',
                'mensagem': f'Falha ao apagar a tabela {nome_tabela}',
                'erro': str(e)
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003)