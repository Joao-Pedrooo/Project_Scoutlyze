# Usar imagem Python oficial como base
FROM python:3.10-slim

# Configuração do diretório de trabalho
WORKDIR /app

# Copiar os arquivos de dependências
COPY requirements.txt .

# Instalar as dependências


RUN pip install --upgrade pip  --no-cache-dir -r requirements.txt

# Copiar todo o código da aplicação para o container
COPY . .

# Expor a porta para acesso à aplicação
EXPOSE 8003

# Comando para iniciar o servidor FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]
