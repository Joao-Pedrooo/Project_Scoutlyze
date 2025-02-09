from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db, Partida, Time
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def listar_partidas(request: Request, db: Session = Depends(get_db)):
    # Ordena as partidas pela data de criação (mais recentes primeiro)
    partidas = db.query(Partida).order_by(Partida.created_at.desc()).all()
    times = db.query(Time).all()
    return templates.TemplateResponse("partidas.html", {
        "request": request,
        "partidas": partidas,
        "times": times
    })

@router.post("/", response_class=RedirectResponse)
def cadastrar_partida(
    time_casa_id: str = Form(...),
    time_visitante_id: str = Form(...),
    campeonato: str = Form(...),
    fase_competicao: str = Form(...),  # "classificatorio" ou "eliminatorio"
    rodada: int = Form(None),
    local_partida: str = Form(None),
    data_partida: str = Form(...),  # Formato YYYY-MM-DD
    placar_casa: int = Form(...),
    placar_visitante: int = Form(...),
    db: Session = Depends(get_db)
):
    # Validação conforme a fase da competição
    if fase_competicao == "classificatorio":
        if rodada is None:
            raise HTTPException(status_code=400, detail="Para jogos classificatórios, informe a rodada (1 a 20).")
        if local_partida is None:
            raise HTTPException(status_code=400, detail="Para jogos classificatórios, informe se o jogo foi realizado em Casa ou Fora.")
        local_partida_val = local_partida  # Armazena o valor informado
    elif fase_competicao == "eliminatorio":
        if local_partida is None:
            raise HTTPException(status_code=400, detail="Para jogos eliminatórios, informe se o jogo foi realizado em Casa ou Fora.")
        rodada = None  # Não utilizamos rodada para eliminatórios.
        local_partida_val = local_partida
    else:
        raise HTTPException(status_code=400, detail="Fase da competição inválida.")

    # Converte a data da partida
    try:
        data_partida_dt = datetime.strptime(data_partida, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Data da partida deve estar no formato YYYY-MM-DD.")

    periodo_val = 1  # Valor padrão para período

    # Verifica se os times existem
    time_casa_obj = db.query(Time).filter(Time.time_id == time_casa_id).first()
    time_visitante_obj = db.query(Time).filter(Time.time_id == time_visitante_id).first()
    if not time_casa_obj or not time_visitante_obj:
        raise HTTPException(status_code=400, detail="Um dos times não existe.")

    nova_partida = Partida(
        time_casa_id=time_casa_id,
        time_visitante_id=time_visitante_id,
        campeonato=campeonato,
        fase_competicao=fase_competicao,
        rodada=rodada,
        local_partida=local_partida_val,
        data_partida=data_partida_dt,
        periodo=periodo_val,
        placar_casa=placar_casa,
        placar_visitante=placar_visitante,
        minuto_acao=0,
        placar_momento="0x0",
        created_at=datetime.now()
    )
    db.add(nova_partida)
    db.commit()
    db.refresh(nova_partida)
    return RedirectResponse(url="/api/partidas/", status_code=303)

@router.get("/editar/{partida_id}", response_class=HTMLResponse)
def exibir_formulario_edicao(partida_id: str, request: Request, db: Session = Depends(get_db)):
    partida = db.query(Partida).filter(Partida.partida_id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida não encontrada.")
    times = db.query(Time).all()
    return templates.TemplateResponse("editar_partida.html", {
        "request": request,
        "partida": partida,
        "times": times
    })

@router.post("/editar/{partida_id}", response_class=RedirectResponse)
def editar_partida(
    partida_id: str,
    time_casa_id: str = Form(...),
    time_visitante_id: str = Form(...),
    campeonato: str = Form(...),
    fase_competicao: str = Form(...),
    rodada: int = Form(None),
    local_partida: str = Form(None),
    data_partida: str = Form(...),
    placar_casa: int = Form(...),
    placar_visitante: int = Form(...),
    db: Session = Depends(get_db)
):
    if fase_competicao == "classificatorio":
        if rodada is None:
            raise HTTPException(status_code=400, detail="Para jogos classificatórios, informe a rodada (1 a 20).")
        if local_partida is None:
            raise HTTPException(status_code=400, detail="Para jogos classificatórios, informe se o jogo foi realizado em Casa ou Fora.")
        local_partida_val = local_partida
    elif fase_competicao == "eliminatorio":
        if local_partida is None:
            raise HTTPException(status_code=400, detail="Para jogos eliminatórios, informe se o jogo foi realizado em Casa ou Fora.")
        rodada = None
        local_partida_val = local_partida
    else:
        raise HTTPException(status_code=400, detail="Fase da competição inválida.")

    try:
        data_partida_dt = datetime.strptime(data_partida, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Data da partida deve estar no formato YYYY-MM-DD.")

    partida = db.query(Partida).filter(Partida.partida_id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida não encontrada.")

    time_casa_obj = db.query(Time).filter(Time.time_id == time_casa_id).first()
    time_visitante_obj = db.query(Time).filter(Time.time_id == time_visitante_id).first()
    if not time_casa_obj or not time_visitante_obj:
        raise HTTPException(status_code=400, detail="Um dos times não existe.")

    partida.time_casa_id = time_casa_id
    partida.time_visitante_id = time_visitante_id
    partida.campeonato = campeonato
    partida.fase_competicao = fase_competicao
    partida.rodada = rodada
    partida.local_partida = local_partida_val
    partida.data_partida = data_partida_dt
    partida.placar_casa = placar_casa
    partida.placar_visitante = placar_visitante

    db.commit()
    db.refresh(partida)
    return RedirectResponse(url="/api/partidas/", status_code=303)

@router.delete("/{partida_id}")
def deletar_partida(partida_id: str, db: Session = Depends(get_db)):
    partida = db.query(Partida).filter(Partida.partida_id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida não encontrada.")
    db.delete(partida)
    db.commit()
    return {"message": "Partida deletada com sucesso."}
