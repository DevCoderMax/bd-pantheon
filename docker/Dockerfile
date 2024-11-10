# Base image
FROM python:3.10-slim

# Define diretório de trabalho
WORKDIR /app

# Copia o arquivo de dependências
COPY ../requirements.txt ./requirements.txt

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o conteúdo da pasta bd_pantheon para o container
COPY ../bd_pantheon/ ./bd_pantheon

# Define a variável de ambiente para o Quart (caso necessário)
ENV QUART_APP=bd_pantheon/api/app.py

# Expõe a porta que a aplicação utiliza
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["quart", "run", "--host", "0.0.0.0", "--port", "5000"]
