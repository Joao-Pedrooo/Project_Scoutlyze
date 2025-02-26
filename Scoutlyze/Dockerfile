# Usa a imagem oficial Python 3.10 no modo "slim" (mais leve)
FROM python:3.10-slim

# Instala dependências do sistema, incluindo o cliente MySQL
RUN apt-get update && \
    apt-get install -y default-mysql-client && \
    rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia o arquivo de dependências para o container
COPY requirements.txt .

# Atualiza pip e instala as dependências
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia todo o código da aplicação para dentro do container
COPY . .

# Expondo a porta onde sua aplicação irá rodar
EXPOSE 8003

# Script de entrada (entrypoint) ou comando principal
CMD ["./entrypoint.sh"]
