import aiohttp
import asyncio

async def executar_consulta():
    # Comando SQL para selecionar todos os dados da tabela 'users'
    comando = {"comando": "SELECT * FROM users"}
    
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:5003/executar-sql', json=comando) as response:
            resultado = await response.json()
            print(resultado)

# Executa a consulta assíncrona
asyncio.run(executar_consulta())