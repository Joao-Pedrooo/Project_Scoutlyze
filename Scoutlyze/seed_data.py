# seed_data_complete.py

from app.database import (
    SessionLocal, Time, Jogador, Partida, Escanteio, EstatisticasJogo,
    ZonaQuadra, ZonaGoleira, TipoAtaque, Evento, Falta, Finalizacao,
    Assistencia, Passe, AcaoDefensiva, Lesao
)
from datetime import datetime, date

def seed_data():
    session = SessionLocal()
    try:
        # 1. Inserção dos Times
        time_yeesco = Time(nome="yeesco", categoria="profissional")
        time_chape = Time(nome="chapecoense", categoria="profissional")
        time_saudades = Time(nome="saudades", categoria="base")
        time_uruguaiana = Time(nome="uruguaiana", categoria="feminino")
        time_cacador = Time(nome="cacador", categoria="profissional")
        session.add_all([time_yeesco, time_chape, time_saudades, time_uruguaiana, time_cacador])
        session.commit()
        print("Times inseridos.")

        # 2. Inserção dos Jogadores
        jogador1 = Jogador(
            time_id=time_yeesco.time_id,
            nome="Jogador 1 Yeesco",
            numero_camisa="10",
            posicao="ala",
            pe_dominante="direito",
            status="ativo",
        )
        jogador2 = Jogador(
            time_id=time_chape.time_id,
            nome="Jogador 2 Chapecoense",
            numero_camisa="09",
            posicao="goleiro",
            pe_dominante="esquerdo",
            status="ativo",
        )
        jogador3 = Jogador(
            time_id=time_saudades.time_id,
            nome="Jogador 3 Saudades",
            numero_camisa="11",
            posicao="fixo",
            pe_dominante="direito",
            status="ativo",
        )
        jogador4 = Jogador(
            time_id=time_uruguaiana.time_id,
            nome="Jogador 4 Uruguaiana",
            numero_camisa="07",
            posicao="pivo",
            pe_dominante="esquerdo",
            status="ativo",
        )
        jogador5 = Jogador(
            time_id=time_cacador.time_id,
            nome="Jogador 5 Cacador",
            numero_camisa="08",
            posicao="ala",
            pe_dominante="direito",
            status="ativo",
        )
        session.add_all([jogador1, jogador2, jogador3, jogador4, jogador5])
        session.commit()
        print("Jogadores inseridos.")

        # 3. Inserção de Zonas (Quadra e Goleira)
        zona_quadra = ZonaQuadra(numero_zona=5)
        zona_goleira = ZonaGoleira(numero_zona_goleira=10)
        session.add_all([zona_quadra, zona_goleira])
        session.commit()
        print("Zonas inseridas.")

        # 4. Inserção de Tipo de Ataque
        tipo_ataque = TipoAtaque(
            nome="ataque_posicional",
            descricao_vantagem="vantagem_numerica",
            periodo=1
        )
        session.add(tipo_ataque)
        session.commit()
        print("Tipo de ataque inserido.")

        # 5. Inserção de uma Partida
        partida = Partida(
            time_casa_id=time_yeesco.time_id,
            time_visitante_id=time_chape.time_id,
            mando_campo="casa",
            data_hora=datetime(2025, 3, 1, 15, 0, 0),
            status_partida="agendada",
            campeonato="campeonato_brasileiro",
            rodada=5,
            placar_casa=0,
            placar_visitante=0,
            periodo=1,
            minuto_acao=10,
            local_jogo="Estádio X"
        )
        session.add(partida)
        session.commit()
        print("Partida inserida.")

        # 6. Estatísticas do Jogo para a Partida
        estatisticas = EstatisticasJogo(
            partida_id=partida.partida_id,
            time_id=time_yeesco.time_id,
            posse_bola=55.50,
            finalizacoes_total=10,
            finalizacoes_no_gol=5,
            faltas_cometidas=3,
            faltas_sofridas=4,
            cartoes_amarelos=1,
            cartoes_vermelhos=0,
            escanteios=2,
            defesas_goleiro=8,
            periodo=1
        )
        session.add(estatisticas)
        session.commit()
        print("Estatísticas inseridas.")

        # 7. Escanteios da Partida
        escanteio = Escanteio(
            partida_id=partida.partida_id,
            escanteios_pro=3,
            escanteios_contra=2,
            periodo=1
        )
        session.add(escanteio)
        session.commit()
        print("Escanteios inseridos.")

        # 8. Evento (ex.: gol) na Partida
        evento = Evento(
            partida_id=partida.partida_id,
            jogador_id=jogador1.jogador_id,
            tipo_evento="gol",
            zona_quadra_id=zona_quadra.zona_quadra_id,
            periodo=1,
            minuto_evento=15
        )
        session.add(evento)
        session.commit()
        print("Evento inserido.")

        # 9. Falta na Partida
        falta = Falta(
            partida_id=partida.partida_id,
            jogador_id=jogador2.jogador_id,
            zona_quadra_id=zona_quadra.zona_quadra_id,
            tipo_falta="sofrida",
            gerou_cartao=False,
            periodo=1
        )
        session.add(falta)
        session.commit()
        print("Falta inserida.")

        # 10. Finalização na Partida
        finalizacao = Finalizacao(
            partida_id=partida.partida_id,
            jogador_id=jogador3.jogador_id,
            zona_quadra_id=zona_quadra.zona_quadra_id,
            zona_goleira_id=zona_goleira.zona_goleira_id,
            tipo_ataque_id=tipo_ataque.tipo_ataque_id,
            periodo=1,
            rebote=False
        )
        session.add(finalizacao)
        session.commit()
        print("Finalização inserida.")

        # 11. Assistência (para a finalização)
        assistencia = Assistencia(
            finalizacao_id=finalizacao.finalizacao_id,
            jogador_id=jogador4.jogador_id,
            jogador_assistido_id=jogador3.jogador_id,
            zona_quadra_id=zona_quadra.zona_quadra_id,
            tipo_ataque_id=tipo_ataque.tipo_ataque_id,
            assistencia_convertida=True,
            periodo=1
        )
        session.add(assistencia)
        session.commit()
        print("Assistência inserida.")

        # 12. Passe na Partida
        passe = Passe(
            partida_id=partida.partida_id,
            jogador_origem_id=jogador5.jogador_id,
            zona_origem_id=zona_quadra.zona_quadra_id,
            zona_destino_id=zona_quadra.zona_quadra_id,
            tipo_passe="rasteiro",
            passe_errado=False,
            tipo_ataque_id=tipo_ataque.tipo_ataque_id,
            periodo=1,
            minuto=20
        )
        session.add(passe)
        session.commit()
        print("Passe inserido.")

        # 13. Ação Defensiva na Partida
        acao_defensiva = AcaoDefensiva(
            partida_id=partida.partida_id,
            jogador_id=jogador2.jogador_id,
            zona_quadra_id=zona_quadra.zona_quadra_id,
            tipo_acao="desarme_cp",
            periodo=1
        )
        session.add(acao_defensiva)
        session.commit()
        print("Ação defensiva inserida.")

        # 14. Lesão para um Jogador
        lesao = Lesao(
            jogador_id=jogador1.jogador_id,
            tipo_lesao="entorse de tornozelo",
            data_inicio=date(2025, 2, 15),
            data_retorno_previsto=date(2025, 3, 1),
            data_retorno_efetivo=None,
            descricao="Lesão leve, recuperação em andamento.",
            parte_corpo="tornozelo",
            gravidade="leve",
            situacao="em_tratamento"
        )
        session.add(lesao)
        session.commit()
        print("Lesão inserida.")

        print("Seed data para todo o banco de dados inserida com sucesso!")
    except Exception as e:
        session.rollback()
        print("Erro ao inserir seed data:", e)
    finally:
        session.close()

if __name__ == "__main__":
    seed_data()
