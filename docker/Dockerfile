# Usa uma imagem base leve com Python 3.11
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos necessários para o diretório de trabalho no container
COPY .. .

# Instala as dependências necessárias
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta padrão que o Quart usa (geralmente 5000)
EXPOSE 5000

# Comando para rodar o servidor
CMD ["python", "api/app.py"]
