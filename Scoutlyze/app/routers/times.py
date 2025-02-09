from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db, Jogador, Time
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse

import random
import string

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Função para gerar ID único no formato TM000000
def gerar_time_id(db: Session):
    while True:
        novo_id = f"TM{''.join(random.choices(string.digits, k=6))}"
        existe = db.query(Time).filter(Time.time_id == novo_id).first()
        if not existe:
            return novo_id

# Função que retorna as categorias com detalhes para exibição no HTML
def get_categorias():
    return [
        {"value": "profissional", "description": "Time profissional (nível máximo de competição)"},
        {"value": "base", "description": "Time de base (foco no desenvolvimento e formação)"},
        {"value": "feminino", "description": "Time feminino (competições exclusivamente femininas)"}
    ]

# ------------------- Rota para Listar Times -------------------
@router.get("/", response_class=HTMLResponse)
def listar_times(request: Request, db: Session = Depends(get_db)):
    times = db.query(Time).all()
    # Inclui as categorias detalhadas no contexto para uso no template
    categorias = get_categorias()
    return templates.TemplateResponse(
        "times.html",
        {"request": request, "times": times, "categorias": categorias}
    )

# ------------------- Rota para Cadastrar um Novo Time -------------------
@router.post("/")
def cadastrar_time(nome: str = Form(...), categoria: str = Form(...), db: Session = Depends(get_db)):
    # Verifica se o nome do time já existe (ignorando maiúsculas/minúsculas)
    existe_time = db.query(Time).filter(func.lower(Time.nome) == func.lower(nome)).first()
    if existe_time:
        raise HTTPException(status_code=400, detail="Time já existe!")

    novo_time = Time(time_id=gerar_time_id(db), nome=nome, categoria=categoria)
    db.add(novo_time)
    db.commit()
    db.refresh(novo_time)
    return RedirectResponse(url="/api/times/", status_code=303)

# ------------------- Rota para Deletar um Time -------------------
@router.delete("/{time_id}")
def deletar_time(time_id: str, db: Session = Depends(get_db)):
    time = db.query(Time).filter(Time.time_id == time_id).first()
    if not time:
        raise HTTPException(status_code=404, detail="Time não encontrado")

    # Verifica se o time possui jogadores antes de deletar
    jogadores_associados = db.query(Jogador).filter(Jogador.time_id == time_id).count()
    if jogadores_associados > 0:
        raise HTTPException(status_code=400, detail="Não é possível deletar um time com jogadores cadastrados!")

    db.delete(time)
    db.commit()
    return {"message": "Time deletado com sucesso"}

# ------------------- Rota para Listar Jogadores de um Time -------------------
@router.get("/{time_id}/jogadores", response_class=HTMLResponse)
def visualizar_jogadores_do_time(time_id: str, request: Request, db: Session = Depends(get_db)):
    time = db.query(Time).filter(Time.time_id == time_id).first()
    if not time:
        raise HTTPException(status_code=404, detail="Time não encontrado")

    jogadores = db.query(Jogador).filter(Jogador.time_id == time_id).all()
    return templates.TemplateResponse(
        "jogadores_do_time.html",
        {"request": request, "time": time, "jogadores": jogadores}
    )
