import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db, Partida, Evento, Finalizacao, Jogador, TipoAtaque

logger = logging.getLogger("jogo_ao_vivo")
logging.basicConfig(level=logging.INFO)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def normalize_tipo_ataque(input_val: str) -> str:
    """
    Converte para minúsculas, removendo espaços e underscores.
    Exemplo: "ataque_posicional" ou "ataque posicional" -> "ataqueposicional"
    """
    return "".join(input_val.lower().replace("_", " ").split())

def validar_evento(minuto: int, periodo: int):
    if minuto < 0 or minuto > 40:
        raise HTTPException(status_code=400, detail="O minuto do evento deve estar entre 0 e 40.")
    if periodo not in (1, 2):
        raise HTTPException(status_code=400, detail="Período inválido. Deve ser 1 ou 2.")

def get_evento_by_id(db: Session, evento_id: str):
    evento = db.query(Evento).filter(Evento.evento_id == evento_id).first()
    if not evento:
        evento = db.query(Finalizacao).filter(Finalizacao.finalizacao_id == evento_id).first()
    return evento

@router.get("/", response_class=HTMLResponse)
def painel_jogos(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    partidas = db.query(Partida).all()
    return templates.TemplateResponse("jogo_ao_vivo.html", {"request": request, "partidas": partidas})

@router.post("/iniciar", response_class=RedirectResponse)
def iniciar_jogo(partida_id: str = Form(...), db: Session = Depends(get_db)) -> RedirectResponse:
    partida = db.query(Partida).filter(Partida.partida_id == partida_id).first()
    if not partida:
        logger.error("Partida %s não encontrada para iniciar o jogo.", partida_id)
        raise HTTPException(status_code=404, detail="Partida não encontrada.")
    return RedirectResponse(url=f"/api/jogo_ao_vivo/{partida_id}", status_code=303)

@router.get("/{partida_id}", response_class=HTMLResponse)
def jogo_ao_vivo_partida(
    partida_id: str,
    request: Request,
    db: Session = Depends(get_db),
    msg: str = Query(None)
) -> HTMLResponse:
    try:
        partida = db.query(Partida).filter(Partida.partida_id == partida_id).first()
        if not partida:
            logger.error("Partida %s não encontrada.", partida_id)
            raise HTTPException(status_code=404, detail="Partida não encontrada.")
        if not (partida.time_casa and partida.time_visitante):
            logger.error("Dados incompletos na partida %s.", partida_id)
            raise HTTPException(status_code=500, detail="Dados da partida incompletos.")

        jogadores_pro = db.query(Jogador).filter(Jogador.time_id == partida.time_casa_id).order_by(Jogador.numero_camisa).all()
        jogadores_adv = db.query(Jogador).filter(Jogador.time_id == partida.time_visitante_id).order_by(Jogador.numero_camisa).all()

        eventos_normais = db.query(Evento).filter(Evento.partida_id == partida_id).all()
        finalizacoes = db.query(Finalizacao).filter(Finalizacao.partida_id == partida_id).all()

        for f in finalizacoes:
            f.evento_id = f.finalizacao_id
            f.tipo_evento = "finalizacao"

        eventos_list = sorted(eventos_normais + finalizacoes, key=lambda e: e.minuto_evento or 0, reverse=True)
        jogadores_all = {j.jogador_id: j for j in (jogadores_pro + jogadores_adv)}

        return templates.TemplateResponse("jogo_ao_vivo_partida.html", {
            "request": request,
            "partida": partida,
            "jogadores_pro": jogadores_pro,
            "jogadores_adv": jogadores_adv,
            "eventos_list": eventos_list,
            "msg": msg,
            "jogadores_all": jogadores_all
        })
    except Exception as e:
        logger.exception("Erro ao exibir jogo ao vivo para a partida %s: %s", partida_id, e)
        raise HTTPException(status_code=500, detail="Erro ao exibir jogo ao vivo.")

@router.post("/{partida_id}/evento", response_class=RedirectResponse)
def salvar_evento(
    partida_id: str,
    categoria_evento: str = Form(...),  # "finalizacao" ou "evento"
    tipo_evento: str = Form(...),         # Para eventos normais: valor permitido (ex: "gol", "assistencias", etc.)
    jogador_id: str = Form(...),
    zona_quadra: str = Form(""),          # Para eventos, se não enviado, default "ZQ0001"
    zona_quadra_final: str = Form(""),    # Para finalizações, obrigatório
    zona_goleira: str = Form(""),         # Para finalizações, obrigatório
    tipo_ataque: str = Form(""),          # Para finalizações, valor esperado (ex: "ataque_posicional")
    rebote: bool = Form(False),
    periodo: int = Form(...),
    minuto_evento: int = Form(...),
    db: Session = Depends(get_db)
):
    validar_evento(minuto_evento, periodo)
    partida = db.query(Partida).filter(Partida.partida_id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida não encontrada.")

    if categoria_evento == "finalizacao":
        if not (zona_quadra and zona_goleira and tipo_ataque):
            raise HTTPException(status_code=400, detail="Para finalizações, informe zona_quadra, zona_goleira e tipo_ataque.")
        jogador = db.query(Jogador).filter(Jogador.jogador_id == jogador_id).first()
        if not jogador:
            raise HTTPException(status_code=404, detail="Jogador não encontrado.")

        tipo_ataque_obj = db.query(TipoAtaque).filter(
            func.lower(TipoAtaque.nome) == tipo_ataque.lower()
        ).first()
        if not tipo_ataque_obj:
            raise HTTPException(status_code=400, detail=f"Tipo de ataque '{tipo_ataque}' inválido.")

        nova_fin = Finalizacao(
            partida_id=partida_id,
            jogador_id=jogador_id,
            zona_quadra_id=zona_quadra,
            zona_goleira_id=zona_goleira,
            tipo_ataque_id=tipo_ataque_obj.tipo_ataque_id,
            periodo=periodo,
            minuto_evento=minuto_evento,
            rebote=rebote
        )
        db.add(nova_fin)
        logger.info("Finalização salva para o jogador %s, tipo_ataque=%s", jogador_id, tipo_ataque)
    else:
        if not zona_quadra:
            zona_quadra = "ZQ0001"
        jogador = db.query(Jogador).filter(Jogador.jogador_id == jogador_id).first()
        if not jogador:
            raise HTTPException(status_code=404, detail="Jogador não encontrado.")
        novo_evt = Evento(
            partida_id=partida_id,
            jogador_id=jogador_id,
            tipo_evento=tipo_evento,
            zona_quadra_id=zona_quadra,
            periodo=periodo,
            minuto_evento=minuto_evento
        )
        db.add(novo_evt)
        logger.info("Evento '%s' salvo para o jogador %s", tipo_evento, jogador_id)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception("Erro ao salvar evento para a partida %s: %s", partida_id, e)
        raise HTTPException(status_code=500, detail="Erro ao salvar evento.")
    return RedirectResponse(url=f"/api/jogo_ao_vivo/{partida_id}?msg=Evento+inserido", status_code=303)

@router.post("/{partida_id}/evento/editar", response_class=RedirectResponse)
def editar_evento(
    partida_id: str,
    evento_id: str = Form(...),
    categoria_evento: str = Form(...),
    jogador_id: str = Form(...),
    zona_quadra: str = Form(""),
    zona_quadra_final: str = Form(""),
    zona_goleira: str = Form(""),
    tipo_ataque: str = Form(""),
    rebote: bool = Form(False),
    periodo: int = Form(...),
    minuto_evento: int = Form(...),
    db: Session = Depends(get_db)
):
    validar_evento(minuto_evento, periodo)
    evt = get_evento_by_id(db, evento_id)
    if not evt:
        raise HTTPException(status_code=404, detail="Evento não encontrado para edição.")
    jogador = db.query(Jogador).filter(Jogador.jogador_id == jogador_id).first()
    if not jogador:
        raise HTTPException(status_code=404, detail="Jogador não encontrado.")

    if isinstance(evt, Finalizacao):
        if zona_quadra_final:
            evt.zona_quadra_id = zona_quadra_final
        if zona_goleira:
            evt.zona_goleira_id = zona_goleira
        if tipo_ataque:
            atk_obj = db.query(TipoAtaque).filter(func.lower(TipoAtaque.nome) == tipo_ataque.lower()).first()
            if not atk_obj:
                raise HTTPException(status_code=400, detail="Tipo de ataque inválido.")
            evt.tipo_ataque_id = atk_obj.tipo_ataque_id
        evt.jogador_id = jogador_id
        evt.periodo = periodo
        evt.minuto_evento = minuto_evento
        evt.rebote = rebote
    else:
        if zona_quadra:
            evt.zona_quadra_id = zona_quadra
        evt.jogador_id = jogador_id
        evt.periodo = periodo
        evt.minuto_evento = minuto_evento

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception("Erro ao editar evento %s para a partida %s: %s", evento_id, partida_id, e)
        raise HTTPException(status_code=500, detail="Erro ao atualizar evento.")
    return RedirectResponse(url=f"/api/jogo_ao_vivo/{partida_id}?msg=Evento+atualizado", status_code=303)

@router.post("/{partida_id}/encerrar", response_class=RedirectResponse)
def encerrar_jogo(partida_id: str, db: Session = Depends(get_db)) -> RedirectResponse:
    partida = db.query(Partida).filter(Partida.partida_id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida não encontrada.")
    partida.status_partida = "finalizada"
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception("Erro ao encerrar a partida %s: %s", partida_id, e)
        raise HTTPException(status_code=500, detail="Erro ao encerrar a partida.")
    return RedirectResponse(url="/api/jogo_ao_vivo/", status_code=303)
