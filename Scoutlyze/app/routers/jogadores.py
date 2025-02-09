from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from app.database import get_db, Jogador, Time
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def listar_jogadores(request: Request, db: Session = Depends(get_db)):
    # Busca todos os jogadores, ordenando pelo campo created_at (mais recentes primeiro)
    jogadores = db.query(Jogador).order_by(Jogador.created_at.desc()).all()
    # Busca todos os times
    times = db.query(Time).all()
    # Agrupa os jogadores por time_id
    grupos = {}
    for jogador in jogadores:
        grupos.setdefault(jogador.time_id, []).append(jogador)
    # Ordena os grupos pelo created_at do primeiro jogador de cada grupo (mais recente primeiro)
    grupos_ordenados = sorted(grupos.items(), key=lambda item: item[1][0].created_at, reverse=True)
    return templates.TemplateResponse("jogadores.html", {
        "request": request,
        "groups": grupos_ordenados,
        "times": times
    })

@router.post("/")
def criar_jogador(
    nome: str = Form(...),
    numero: int = Form(...),
    posicao: str = Form(...),
    pe_dominante: str = Form(...),
    time_id: str = Form(...),
    db: Session = Depends(get_db)
):
    # Regra de formatação para o nome:
    # Se o nome tiver 1 ou 2 caracteres, todas as letras serão maiúsculas;
    # caso contrário, cada palavra inicia com letra maiúscula.
    if len(nome.strip()) <= 2:
        nome_formatado = nome.strip().upper()
    else:
        nome_formatado = nome.strip().title()

    novo_jogador = Jogador(
        nome=nome_formatado,
        numero_camisa=str(numero).zfill(2),
        posicao=posicao,
        pe_dominante=pe_dominante,
        time_id=time_id,
    )
    db.add(novo_jogador)
    db.commit()
    db.refresh(novo_jogador)
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
    times = db.query(Time).all()
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
    db: Session = Depends(get_db)
):
    jogador = db.query(Jogador).filter(Jogador.jogador_id == jogador_id).first()
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado.")

    if len(nome.strip()) <= 2:
        nome_formatado = nome.strip().upper()
    else:
        nome_formatado = nome.strip().title()

    jogador.nome = nome_formatado
    jogador.numero_camisa = str(numero).zfill(2)
    jogador.posicao = posicao
    jogador.pe_dominante = pe_dominante
    jogador.time_id = time_id
    db.commit()
    db.refresh(jogador)
    return RedirectResponse(url="/api/jogadores", status_code=303)
