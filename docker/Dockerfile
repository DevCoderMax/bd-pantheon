# Use uma imagem base com Python
FROM python:3.10-slim

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o código-fonte da API para o diretório do contêiner
COPY . /app

# Instalar as dependências do requirements.txt
# Certifique-se de que seu requirements.txt está atualizado com todas as dependências necessárias
RUN pip install --no-cache-dir -r requirements.txt

# Se necessário, defina variáveis de ambiente, como para o banco de dados
# ENV DB_HOST=seu_host_do_banco_de_dados

# Exponha a porta que a API vai usar
EXPOSE 5000

# Defina o comando para rodar a API, no caso, Quart com Uvicorn
CMD ["quart", "run", "--host", "0.0.0.0", "--port", "5000"]
