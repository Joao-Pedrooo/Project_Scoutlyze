from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db, Jogador, Time  # Ajuste o caminho conforme sua estrutura
import random
import string

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def listar_jogadores(request: Request, db: Session = Depends(get_db)):
    # Recupera os jogadores em ordem decrescente (último inserido primeiro)
    jogadores = db.query(Jogador).order_by(Jogador.jogador_id.desc()).all()
    # Recupera os times em ordem ascendente
    times = db.query(Time).order_by(Time.time_id.asc()).all()

    # Agrupa os jogadores por time_id para facilitar a exibição
    grupos = {}
    for jogador in jogadores:
        grupos.setdefault(jogador.time_id, []).append(jogador)
    grupos_ordenados = sorted(grupos.items(), key=lambda item: item[0])

    return templates.TemplateResponse("jogadores.html", {
        "request": request,
        "groups": grupos_ordenados,
        "times": times,
        "jogadores": jogadores
    })

@router.post("/")
def criar_jogador(
    nome: str = Form(...),
    numero: int = Form(...),
    posicao: str = Form(...),
    pe_dominante: str = Form(...),
    time_id: str = Form(...),
    data_nascimento: str = Form(None),
    altura: float = Form(None),
    peso: float = Form(None),
    nacionalidade: str = Form(None),
    status: str = Form(...),
    tempo_jogo: int = Form(None),
    db: Session = Depends(get_db)
):
    # Formata o nome: se tiver 1 ou 2 caracteres, converte para maiúsculas; caso contrário, capitaliza cada palavra.
    if len(nome.strip()) <= 2:
        nome_formatado = nome.strip().upper()
    else:
        nome_formatado = nome.strip().title()

    # Converte data de nascimento se fornecida (formato ISO: YYYY-MM-DD)
    if data_nascimento:
        try:
            data_nascimento_parsed = date.fromisoformat(data_nascimento)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Data de nascimento inválida. Use o formato YYYY-MM-DD."
            )
    else:
        data_nascimento_parsed = None

    novo_jogador = Jogador(
        nome=nome_formatado,
        numero_camisa=str(numero).zfill(2),
        posicao=posicao,
        pe_dominante=pe_dominante,
        time_id=time_id,
        data_nascimento=data_nascimento_parsed,
        altura=altura,     # Valor numérico, deve seguir o padrão (por exemplo, 1.70)
        peso=peso,         # Valor numérico (por exemplo, 70.0)
        nacionalidade=nacionalidade,
        status=status,
        tempo_jogo=tempo_jogo
    )
    db.add(novo_jogador)
    db.commit()
    return RedirectResponse(url="/api/jogadores", status_code=303)

@router.delete("/{jogador_id}")
def deletar_jogador(jogador_id: str, db: Session = Depends(get_db)):
    jogador = db.query(Jogador).filter(Jogador.jogador_id == jogador_id).first()
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado.")
    db.delete(jogador)
    db.commit()
    return {"message": "Jogador deletado com sucesso!"}

@router.get("/editar/{jogador_id}", response_class=HTMLResponse)
def exibir_formulario_edicao(jogador_id: str, request: Request, db: Session = Depends(get_db)):
    jogador = db.query(Jogador).filter(Jogador.jogador_id == jogador_id).first()
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado.")
    times = db.query(Time).order_by(Time.time_id.asc()).all()
    return templates.TemplateResponse("editar_jogador.html", {
        "request": request,
        "jogador": jogador,
        "times": times
    })

@router.post("/editar/{jogador_id}")
def editar_jogador(
    jogador_id: str,
    nome: str = Form(...),
    numero: int = Form(...),
    posicao: str = Form(...),
    pe_dominante: str = Form(...),
    time_id: str = Form(...),
    data_nascimento: str = Form(None),
    altura: float = Form(None),
    peso: float = Form(None),
    nacionalidade: str = Form(None),
    status: str = Form(...),
    tempo_jogo: int = Form(0),
    db: Session = Depends(get_db)
):
    jogador = db.query(Jogador).filter(Jogador.jogador_id == jogador_id).first()
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado.")

    if len(nome.strip()) <= 2:
        nome_formatado = nome.strip().upper()
    else:
        nome_formatado = nome.strip().title()

    if data_nascimento:
        try:
            data_nascimento_parsed = date.fromisoformat(data_nascimento)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Data de nascimento inválida. Use o formato YYYY-MM-DD."
            )
    else:
        data_nascimento_parsed = None

    jogador.nome = nome_formatado
    jogador.numero_camisa = str(numero).zfill(2)
    jogador.posicao = posicao
    jogador.pe_dominante = pe_dominante
    jogador.time_id = time_id
    jogador.data_nascimento = data_nascimento_parsed
    jogador.altura = altura
    jogador.peso = peso
    jogador.nacionalidade = nacionalidade
    jogador.status = status
    jogador.tempo_jogo = tempo_jogo

    db.commit()
    return RedirectResponse(url="/api/jogadores", status_code=303)
