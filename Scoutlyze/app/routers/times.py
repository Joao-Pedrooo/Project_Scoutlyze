from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, text
import random
import string

from app.database import get_db, Time, Jogador  # Ajuste o caminho conforme sua estrutura

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_categorias():
    return [
        {"value": "profissional", "description": "Time profissional (nível máximo de competição)"},
        {"value": "base", "description": "Time de base (foco no desenvolvimento e formação)"},
        {"value": "feminino", "description": "Time feminino (competições exclusivamente femininas)"}
    ]

ALLOWED_NAMES = {"yeesco", "chapecoense", "saudades", "uruguaiana", "cacador"}

@router.get("/", response_class=HTMLResponse)
def listar_times(request: Request, db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar ao banco: {str(e)}")
    # Ordena os times pelo campo time_id (ordem ascendente)
    times = db.query(Time).order_by(Time.time_id.asc()).all()
    categorias = get_categorias()
    return templates.TemplateResponse("times.html", {
        "request": request,
        "times": times,
        "categorias": categorias
    })

@router.post("/")
def cadastrar_time(nome: str = Form(...), categoria: str = Form(...), db: Session = Depends(get_db)):
    if nome.lower() not in ALLOWED_NAMES:
        raise HTTPException(
            status_code=400,
            detail=f"Nome de time inválido! Utilize um dos seguintes: {', '.join(sorted(ALLOWED_NAMES))}"
        )

    existe_time = db.query(Time).filter(func.lower(Time.nome) == func.lower(nome)).first()
    if existe_time:
        raise HTTPException(status_code=400, detail="Time já existe!")

    novo_time = Time(
        # Como o ID é gerado automaticamente pelo banco, não o informamos aqui
        nome=nome.lower(),
        categoria=categoria
    )
    db.add(novo_time)
    db.commit()
    return RedirectResponse(url="/api/times/", status_code=303)

@router.delete("/{time_id}")
def deletar_time(time_id: str, db: Session = Depends(get_db)):
    time = db.query(Time).filter(Time.time_id == time_id).first()
    if not time:
        raise HTTPException(status_code=404, detail="Time não encontrado")
    # Impede a exclusão se houver jogadores vinculados
    jogadores_associados = db.query(Jogador).filter(Jogador.time_id == time_id).count()
    if jogadores_associados > 0:
        raise HTTPException(status_code=400, detail="Não é possível deletar um time com jogadores cadastrados!")
    db.delete(time)
    db.commit()
    return {"message": "Time deletado com sucesso"}

@router.get("/{time_id}/jogadores", response_class=HTMLResponse)
def visualizar_jogadores_do_time(time_id: str, request: Request, db: Session = Depends(get_db)):
    time = db.query(Time).filter(Time.time_id == time_id).first()
    if not time:
        raise HTTPException(status_code=404, detail="Time não encontrado")
    # Ordena os jogadores do time em ordem decrescente pelo ID (último inserido primeiro)
    jogadores = db.query(Jogador).filter(Jogador.time_id == time_id).order_by(Jogador.jogador_id.desc()).all()
    return templates.TemplateResponse("jogadores_do_time.html", {
        "request": request,
        "time": time,
        "jogadores": jogadores
    })
