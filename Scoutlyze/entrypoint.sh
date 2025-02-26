#!/bin/bash
echo "Iniciando a aplicação... (Banco remoto configurado)"


# Opcional: Executar seed_data.py se necessário
#python seed_data.py

# Inicia o servidor FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
