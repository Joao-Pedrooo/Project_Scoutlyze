# app/routers/partidas.py
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db, Partida, Time

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def listar_partidas(request: Request, db: Session = Depends(get_db)):
    """
    Lista as partidas ordenadas por data/hora (decrescente) e fornece os times para o formulário.
    """
    partidas = db.query(Partida).order_by(Partida.data_hora.desc()).all()
    times = db.query(Time).order_by(Time.time_id.asc()).all()
    return templates.TemplateResponse(
        "partidas.html",
        {"request": request, "partidas": partidas, "times": times}
    )

@router.post("/")
def criar_partida(
    time_casa_id: str = Form(...),
    time_visitante_id: str = Form(...),
    mando_campo: str = Form(...),
    data_hora: str = Form(...),  # Espera formato "YYYY-MM-DDTHH:MM"
    status_partida: str = Form(...),
    campeonato: str = Form(...),
    rodada: int = Form(...),
    placar_casa: int = Form(0),
    placar_visitante: int = Form(0),
    periodo: int = Form(...),
    minuto_acao: str = Form(None),  # Pode vir vazio
    local_jogo: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Cria uma nova partida a partir dos dados do formulário.
    Converte a data/hora e trata o campo minuto_acao (definindo 0 caso vazio).
    """
    try:
        data_dt = datetime.strptime(data_hora, "%Y-%m-%dT%H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de data/hora inválido. Use YYYY-MM-DDTHH:MM")

    # Trata o campo minuto_acao: se estiver vazio, define 0
    if minuto_acao is None or minuto_acao.strip() == "":
        minuto_acao_int = 0
    else:
        try:
            minuto_acao_int = int(minuto_acao)
        except ValueError:
            raise HTTPException(status_code=400, detail="Minuto da ação deve ser um número inteiro.")

    nova_partida = Partida(
        time_casa_id=time_casa_id,
        time_visitante_id=time_visitante_id,
        mando_campo=mando_campo,
        data_hora=data_dt,
        status_partida=status_partida,
        campeonato=campeonato,
        rodada=rodada,
        placar_casa=placar_casa,
        placar_visitante=placar_visitante,
        periodo=periodo,
        minuto_acao=minuto_acao_int,
        local_jogo=local_jogo
    )
    db.add(nova_partida)
    db.commit()
    # db.refresh(nova_partida)  # Removido para evitar erro de refresh
    return RedirectResponse(url="/api/partidas/", status_code=303)

@router.get("/editar/{partida_id}", response_class=HTMLResponse)
def exibir_formulario_edicao(partida_id: str, request: Request, db: Session = Depends(get_db)):
    """
    Exibe o formulário de edição para a partida com o ID fornecido.
    """
    partida = db.query(Partida).filter(Partida.partida_id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida não encontrada.")
    times = db.query(Time).order_by(Time.time_id.asc()).all()
    return templates.TemplateResponse(
        "editar_partida.html",
        {"request": request, "partida": partida, "times": times}
    )

@router.post("/editar/{partida_id}")
def editar_partida(
    partida_id: str,
    time_casa_id: str = Form(...),
    time_visitante_id: str = Form(...),
    mando_campo: str = Form(...),
    data_hora: str = Form(...),
    status_partida: str = Form(...),
    campeonato: str = Form(...),
    rodada: int = Form(...),
    placar_casa: int = Form(0),
    placar_visitante: int = Form(0),
    periodo: int = Form(...),
    minuto_acao: str = Form("0"),
    local_jogo: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Atualiza os dados de uma partida existente.
    """
    partida = db.query(Partida).filter(Partida.partida_id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida não encontrada.")

    try:
        data_dt = datetime.strptime(data_hora, "%Y-%m-%dT%H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de data/hora inválido. Use YYYY-MM-DDTHH:MM")

    if minuto_acao is None or minuto_acao.strip() == "":
        minuto_acao_int = 0
    else:
        try:
            minuto_acao_int = int(minuto_acao)
        except ValueError:
            raise HTTPException(status_code=400, detail="Minuto da ação deve ser um número inteiro.")

    partida.time_casa_id = time_casa_id
    partida.time_visitante_id = time_visitante_id
    partida.mando_campo = mando_campo
    partida.data_hora = data_dt
    partida.status_partida = status_partida
    partida.campeonato = campeonato
    partida.rodada = rodada
    partida.placar_casa = placar_casa
    partida.placar_visitante = placar_visitante
    partida.periodo = periodo
    partida.minuto_acao = minuto_acao_int
    partida.local_jogo = local_jogo

    db.commit()
    return RedirectResponse(url="/api/partidas/", status_code=303)

@router.delete("/{partida_id}")
def deletar_partida(partida_id: str, db: Session = Depends(get_db)):
    """
    Exclui a partida identificada por 'partida_id'.
    """
    partida = db.query(Partida).filter(Partida.partida_id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida não encontrada.")
    db.delete(partida)
    db.commit()
    return {"message": "Partida deletada com sucesso!"}
