# Etapa 1: Escolher a imagem base (neste caso, uma imagem Python)
FROM python:3.9-slim

# Etapa 2: Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# Etapa 3: Copiar o arquivo requirements.txt (se houver) para o contêiner
COPY requirements.txt .

# Etapa 4: Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Etapa 5: Copiar o arquivo app.py para o diretório de trabalho no contêiner
COPY app.py .

# Etapa 6: Expor a porta que sua aplicação vai usar (Ex: 5000 para Flask)
EXPOSE 5000

# Etapa 7: Definir o comando para rodar a aplicação (no caso de um app Flask)
CMD ["python", "app.py"]
