from fastapi import FastAPI
from app.database import Base, engine
from app.routers import homes, jogadores, times, jogo_ao_vivo, partidas
from fastapi.staticfiles import StaticFiles


# descricao
descrição = '''
    ## Description
        -ProScout

'''

# Inicializa o app FastAPI
app = FastAPI(title="ProScout", version="1.0.0")

# Configurando o diretório 'static'
app.mount("/static", StaticFiles(directory="app/static"), name="static")
# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Inclui as rotas
app.include_router(homes.router, tags=["Home"])
app.include_router(times.router, prefix="/api/times", tags=["Times"])
app.include_router(jogadores.router, prefix="/api/jogadores", tags=["Jogadores"])
app.include_router(jogo_ao_vivo.router, prefix="/api/jogo_ao_vivo", tags=["Jogo ao Vivo"])
app.include_router(partidas.router, prefix="/api/partidas", tags=["Partidas"])





