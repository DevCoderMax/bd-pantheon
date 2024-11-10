import requests

# Modifique o comando SQL para selecionar todos os dados da tabela 'users'
command = {"command": "SELECT * FROM users"}
response = requests.post('http://localhost:5000/execute_sql', json=command)
print(response.json())