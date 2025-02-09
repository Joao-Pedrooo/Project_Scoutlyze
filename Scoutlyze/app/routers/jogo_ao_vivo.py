from fastapi import APIRouter, Depends, HTTPException, Request, Form, Query
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from app.database import get_db, Partida, Evento, Finalizacao, Jogador

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def painel_jogos(request: Request, db: Session = Depends(get_db)):
    """
    Exibe o painel com todas as partidas disponíveis.
    """
    partidas = db.query(Partida).all()
    return templates.TemplateResponse("jogo_ao_vivo.html", {"request": request, "partidas": partidas})


@router.post("/iniciar", response_class=RedirectResponse)
def iniciar_jogo(partida_id: str = Form(...), db: Session = Depends(get_db)):
    """
    Inicia um jogo ao vivo com base na partida selecionada.
    """
    partida = db.query(Partida).filter(Partida.partida_id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida não encontrada.")
    return RedirectResponse(url=f"/api/jogo_ao_vivo/{partida_id}", status_code=303)


@router.get("/{partida_id}", response_class=HTMLResponse)
def jogo_ao_vivo_partida(
    partida_id: str,
    request: Request,
    db: Session = Depends(get_db),
    msg: str = Query(None)
):
    """
    Exibe a página do jogo ao vivo com:
      - Dados da partida
      - Jogadores de cada time (ordenados pelo número da camisa)
      - Eventos registrados (eventos genéricos e finalizações)
    """
    # Busca a partida
    partida = db.query(Partida).filter(Partida.partida_id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida não encontrada.")

    # Recupera jogadores dos dois times
    jogadores_pro = (
        db.query(Jogador)
        .filter(Jogador.time_id == partida.time_casa_id)
        .order_by(Jogador.numero_camisa)
        .all()
    )
    jogadores_adv = (
        db.query(Jogador)
        .filter(Jogador.time_id == partida.time_visitante_id)
        .order_by(Jogador.numero_camisa)
        .all()
    )

    # Recupera eventos e finalizações
    eventos_gen = db.query(Evento).filter(Evento.partida_id == partida_id).all()
    finalizacoes = db.query(Finalizacao).filter(Finalizacao.partida_id == partida_id).all()

    # Para finalizações, atribuir valores padrão se os atributos não existirem
    for f in finalizacoes:
        f.minuto_evento = getattr(f, 'minuto_evento', 0)
        f.subtipo_evento = getattr(f, 'subtipo_evento', f.tipo_finalizacao)
        f.parte_corpo = getattr(f, 'parte_corpo', "pe_direito")
        f.situacao_jogo = getattr(f, 'situacao_jogo', "regular")

    # Mescla e ordena eventos (ordem decrescente por minuto)
    eventos = sorted(eventos_gen + finalizacoes, key=lambda e: getattr(e, 'minuto_evento', 0), reverse=True)

    return templates.TemplateResponse("jogo_ao_vivo_partida.html", {
        "request": request,
        "partida": partida,
        "jogadores_pro": jogadores_pro,
        "jogadores_adv": jogadores_adv,
        "eventos": eventos,
        "msg": msg
    })


@router.post("/{partida_id}/evento", response_class=RedirectResponse)
def salvar_evento(
    partida_id: str,
    categoria_evento: str = Form(...),  # Ex.: "finalizacao" ou "evento"
    jogador_id: str = Form(...),
    subtipo_evento: str = Form(None),
    parte_corpo: str = Form(None),
    zona_quadra: str = Form(None),
    periodo: int = Form(...),
    minuto_evento: int = Form(...),
    situacao_jogo: str = Form(None),
    zona_quadra_final: str = Form(None),
    zona_goleira: str = Form(None),
    tipo_ataque: str = Form(None),
    resultado: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Salva um evento para a partida.
    - Se for finalização, atualiza o placar e exige campos extras.
    - Caso contrário, registra um evento genérico.
    """
    if not subtipo_evento:
        subtipo_evento = "outro"

    # Valida a existência da partida
    partida = db.query(Partida).filter(Partida.partida_id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida não encontrada.")

    if categoria_evento == "finalizacao":
        # Campos obrigatórios para finalização
        if not (zona_quadra_final and zona_goleira and tipo_ataque and resultado):
            raise HTTPException(status_code=400, detail="Campos obrigatórios para Finalização não preenchidos.")
        # Busca o jogador finalizador
        finalizador = db.query(Jogador).filter(Jogador.jogador_id == jogador_id).first()
        if not finalizador:
            raise HTTPException(status_code=404, detail="Jogador não encontrado.")

        # Atualiza o placar conforme o time do finalizador
        if finalizador.time_id == partida.time_casa_id:
            partida.placar_casa += 1
        else:
            partida.placar_visitante += 1
        partida.placar_momento = f"{partida.placar_casa}x{partida.placar_visitante}"

        novo_evento = Finalizacao(
            partida_id=partida_id,
            jogador_id=jogador_id,
            zona_quadra_id=zona_quadra_final,
            zona_goleira_id=zona_goleira,
            tipo_ataque_id=tipo_ataque,
            tipo_finalizacao=resultado,
            periodo=periodo
        )
        db.add(novo_evento)
    else:
        novo_evento = Evento(
            partida_id=partida_id,
            jogador_id=jogador_id,
            tipo_evento=categoria_evento,
            subtipo_evento=subtipo_evento,
            parte_corpo=parte_corpo if parte_corpo else "pe_direito",
            zona_quadra_id=zona_quadra if zona_quadra else "ZQ0001",
            periodo=periodo,
            minuto_evento=minuto_evento,
            situacao_jogo=situacao_jogo if situacao_jogo else "regular"
        )
        db.add(novo_evento)

    db.commit()
    return RedirectResponse(url=f"/api/jogo_ao_vivo/{partida_id}?msg=Evento+inserido", status_code=303)


@router.post("/{partida_id}/encerrar", response_class=RedirectResponse)
def encerrar_jogo(partida_id: str, db: Session = Depends(get_db)):
    """
    Encerra o jogo e redireciona para o painel de partidas.
    """
    partida = db.query(Partida).filter(Partida.partida_id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida não encontrada.")
    return RedirectResponse(url="/api/jogo_ao_vivo/", status_code=303)
