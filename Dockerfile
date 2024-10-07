# Use uma imagem base do Python
FROM python:3.10

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o arquivo de dependências
COPY requirements.txt .

# Instale as dependências da aplicação
RUN pip install -r requirements.txt

# Copie o código da aplicação para o contêiner
COPY . .

# Exponha a porta 5003 (a porta usada pela aplicação Flask)
EXPOSE 5003

# Comando para rodar a aplicação
CMD ["python", "app.py"]
