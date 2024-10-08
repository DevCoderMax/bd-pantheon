import requests
import json

# URL base da sua API
BASE_URL = "http://localhost:5003"  # Ajuste conforme necessário

def testar_criar_tabela():
    # Endpoint para criar tabela
    url = f"{BASE_URL}/criar-tabela"

    # Dados para criar a tabela
    dados = {
        "nome_tabela": "controle_dbs",
        "colunas": [
            {"nome": "id", "tipo": "INT AUTO_INCREMENT PRIMARY KEY"},
            {"nome": "numero", "tipo": "VARCHAR(20) NOT NULL"},
            {"nome": "instituicao", "tipo": "VARCHAR(255) NOT NULL"},
            {"nome": "data_adicao", "tipo": "DATE NOT NULL"}
        ]
    }

    # Fazendo a requisição POST
    resposta = requests.post(url, json=dados)

    # Verificando a resposta
    if resposta.status_code == 201:
        print("Tabela criada com sucesso!")
        print(json.dumps(resposta.json(), indent=2))
    else:
        print("Erro ao criar tabela:")
        print(json.dumps(resposta.json(), indent=2))

    # Testando listar tabelas para confirmar a criação
    listar_tabelas()

def listar_tabelas():
    url = f"{BASE_URL}/listar-tabelas"
    resposta = requests.get(url)

    if resposta.status_code == 200:
        print("\nTabelas no banco de dados:")
        print(json.dumps(resposta.json(), indent=2))
    else:
        print("Erro ao listar tabelas:")
        print(json.dumps(resposta.json(), indent=2))

if __name__ == "__main__":
    testar_criar_tabela()