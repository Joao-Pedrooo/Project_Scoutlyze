import os
import random
import string
from dotenv import load_dotenv

from sqlalchemy import (
    Column, String, Integer, ForeignKey, Enum, Boolean, DECIMAL,
    Date, Text, DateTime, create_engine, CheckConstraint, MetaData
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Carrega variáveis de ambiente do .env
load_dotenv()

# Configurações de conexão MySQL
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB", "futsal_analysis")
# Se houver @ na senha, substitua por %40
MYSQL_PASSWORD = MYSQL_PASSWORD.replace("@", "%40")
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

# Define naming convention para constraints e índices
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

# Cria o engine e a sessão
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Função para gerar IDs com prefixo
def gerar_id(prefixo, tamanho=6):
    return f"{prefixo}{''.join(random.choices(string.digits, k=tamanho))}"

# ---------------------------
# MODELOS PRINCIPAIS
# ---------------------------

class Time(Base):
    __tablename__ = "times"
    time_id = Column(String(8), primary_key=True, default=lambda: gerar_id("TM", 6))
    nome = Column(Enum("yeesco", "chapecoense", "saudades", "uruguaiana", "cacador", name="nome_time_enum"), nullable=False)
    categoria = Column(Enum("profissional", "base", "feminino", name="categoria_enum"), nullable=False)

    jogadores = relationship("Jogador", back_populates="time", cascade="all, delete-orphan")
    partidas_casa = relationship("Partida", foreign_keys="[Partida.time_casa_id]", back_populates="time_casa", cascade="all, delete-orphan")
    partidas_visitante = relationship("Partida", foreign_keys="[Partida.time_visitante_id]", back_populates="time_visitante", cascade="all, delete-orphan")


class Jogador(Base):
    __tablename__ = "jogadores"
    jogador_id = Column(String(8), primary_key=True, default=lambda: gerar_id("JG", 6))
    time_id = Column(String(8), ForeignKey("times.time_id", onupdate="CASCADE"), nullable=False)
    nome = Column(String(100), nullable=False)
    numero_camisa = Column(String(2), nullable=False)
    posicao = Column(Enum("goleiro", "fixo", "ala", "pivo", name="posicao_enum"), nullable=False)
    pe_dominante = Column(String(20), nullable=True)
    data_nascimento = Column(Date, nullable=True)
    altura = Column(DECIMAL(3, 2), nullable=True)
    peso = Column(DECIMAL(4, 1), nullable=True)
    nacionalidade = Column(String(50), nullable=True)
    status = Column(Enum("ativo", "lesionado", "suspenso", "inativo", name="status_enum"),
                    nullable=False, default="ativo")
    tempo_jogo = Column(Integer, nullable=True)

    __table_args__ = (
        CheckConstraint("numero_camisa REGEXP '^[0-9]{2}$'", name="ck_jogadores_numero_camisa"),
    )

    time = relationship("Time", back_populates="jogadores")
    eventos_principal = relationship("Evento", foreign_keys="[Evento.jogador_id]", back_populates="jogador_principal")
    lesoes = relationship("Lesao", back_populates="jogador", cascade="all, delete-orphan")


class Partida(Base):
    __tablename__ = "partidas"
    partida_id = Column(String(12), primary_key=True, default=lambda: gerar_id("PT", 6))
    time_casa_id = Column(String(8), ForeignKey("times.time_id", onupdate="CASCADE"), nullable=False)
    time_visitante_id = Column(String(8), ForeignKey("times.time_id", onupdate="CASCADE"), nullable=False)
    mando_campo = Column(Enum("casa", "fora", name="mando_campo_enum"), nullable=False)
    data_hora = Column(DateTime, nullable=False)
    status_partida = Column(Enum("agendada", "em_andamento", "finalizada", name="status_partida_enum"),
                            nullable=False, default="agendada")
    campeonato = Column(Enum("campeonato_brasileiro", "campeonato_catarinense_ouro",
                               "campeonato_catarinense_prata", "campeonato_gaucho",
                               "copa_sc", "copa_rs", "copa_local_rs", name="campeonato_enum"), nullable=False)
    rodada = Column(Integer, nullable=False)
    placar_casa = Column(Integer, nullable=False, default=0)
    placar_visitante = Column(Integer, nullable=False, default=0)
    periodo = Column(Integer, nullable=False)
    minuto_acao = Column(Integer, nullable=True)
    local_jogo = Column(String(100), nullable=True)

    __table_args__ = (
        CheckConstraint("rodada BETWEEN 1 AND 21", name="ck_partidas_rodada"),
        CheckConstraint("periodo IN (1,2)", name="ck_partidas_periodo"),
        CheckConstraint("minuto_acao IS NULL OR minuto_acao BETWEEN 0 AND 40", name="ck_partidas_minuto_acao"),
    )

    time_casa = relationship("Time", foreign_keys=[time_casa_id], back_populates="partidas_casa")
    time_visitante = relationship("Time", foreign_keys=[time_visitante_id], back_populates="partidas_visitante")
    escanteios = relationship("Escanteio", back_populates="partida", cascade="all, delete-orphan")
    estatisticas = relationship("EstatisticasJogo", back_populates="partida", cascade="all, delete-orphan")
    finalizacoes = relationship("Finalizacao", back_populates="partida", cascade="all, delete-orphan")
    eventos = relationship("Evento", back_populates="partida", cascade="all, delete-orphan")
    faltas = relationship("Falta", back_populates="partida", cascade="all, delete-orphan")
    passes = relationship("Passe", back_populates="partida", cascade="all, delete-orphan")
    acoes_defensivas = relationship("AcaoDefensiva", back_populates="partida", cascade="all, delete-orphan")

# ---------------------------
# MODELO ESCANTEIOS
# ---------------------------
class Escanteio(Base):
    __tablename__ = "escanteios"
    escanteio_id = Column(String(12), primary_key=True, default=lambda: gerar_id("ES", 6))
    partida_id = Column(String(12), ForeignKey("partidas.partida_id", onupdate="CASCADE"), nullable=False)
    escanteios_pro = Column(Integer, nullable=False, default=0)
    escanteios_contra = Column(Integer, nullable=False, default=0)
    periodo = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("periodo IN (1,2)", name="ck_escanteios_periodo"),
    )

    partida = relationship("Partida", back_populates="escanteios")

# ---------------------------
# MODELOS DE APOIO
# ---------------------------

class EstatisticasJogo(Base):
    __tablename__ = "estatisticas_jogo"
    estatistica_id = Column(String(12), primary_key=True, default=lambda: gerar_id("EJ", 6))
    partida_id = Column(String(12), ForeignKey("partidas.partida_id", onupdate="CASCADE"), nullable=False)
    time_id = Column(String(8), ForeignKey("times.time_id", onupdate="CASCADE"), nullable=False)
    posse_bola = Column(DECIMAL(5, 2), nullable=False)
    finalizacoes_total = Column(Integer, nullable=False, default=0)
    finalizacoes_no_gol = Column(Integer, nullable=False, default=0)
    faltas_cometidas = Column(Integer, nullable=False, default=0)
    faltas_sofridas = Column(Integer, nullable=False, default=0)
    cartoes_amarelos = Column(Integer, nullable=False, default=0)
    cartoes_vermelhos = Column(Integer, nullable=False, default=0)
    escanteios = Column(Integer, nullable=False, default=0)
    defesas_goleiro = Column(Integer, nullable=False, default=0)
    periodo = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("periodo IN (1,2)", name="ck_estatisticas_periodo"),
    )

    partida = relationship("Partida", back_populates="estatisticas")


class ZonaQuadra(Base):
    __tablename__ = "zonas_quadra"
    zona_quadra_id = Column(String(6), primary_key=True, default=lambda: gerar_id("ZQ", 4))
    numero_zona = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("numero_zona BETWEEN 1 AND 12", name="ck_zonas_quadra_numero_zona"),
    )


class ZonaGoleira(Base):
    __tablename__ = "zonas_goleira"
    zona_goleira_id = Column(String(6), primary_key=True, default=lambda: gerar_id("ZG", 4))
    numero_zona_goleira = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("numero_zona_goleira BETWEEN 1 AND 16", name="ck_zonas_goleira_numero"),
    )


class TipoAtaque(Base):
    __tablename__ = "tipos_ataque"
    tipo_ataque_id = Column(String(6), primary_key=True, default=lambda: gerar_id("TA", 4))
    nome = Column(Enum("ataque_posicional", "ataque_rapido", "contra_ataque", "lateral",
                       "falta", "tiro_livre", "penalti", "escanteio", "5x4",
                       "goleiro_linha", "gol_contra", name="tipo_ataque_enum"), nullable=False)
    descricao_vantagem = Column(Enum("vantagem_numerica", "desvantagem_numerica", "equidade_numerica",
                                     name="descricao_vantagem_enum"), nullable=False)
    periodo = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("periodo IN (1,2)", name="ck_tipos_ataque_periodo"),
    )


# ---------------------------
# MODELOS DE EVENTOS E AÇÕES
# ---------------------------

class Evento(Base):
    __tablename__ = "eventos"
    evento_id = Column(String(12), primary_key=True, default=lambda: gerar_id("EV", 6))
    partida_id = Column(String(12), ForeignKey("partidas.partida_id", onupdate="CASCADE"), nullable=False)
    jogador_id = Column(String(8), ForeignKey("jogadores.jogador_id", onupdate="CASCADE"), nullable=False)
    tipo_evento = Column(Enum("gol", "finalizacoes_certas", "finalizacoes_erradas", "escanteios",
                              "assistencias", "faltas", "passes", name="tipo_evento_enum"), nullable=True)
    zona_quadra_id = Column(String(6), ForeignKey("zonas_quadra.zona_quadra_id", onupdate="CASCADE"), nullable=False)
    periodo = Column(Integer, nullable=False)
    minuto_evento = Column(Integer, nullable=True)

    __table_args__ = (
        CheckConstraint("periodo IN (1,2)", name="ck_eventos_periodo"),
        CheckConstraint("minuto_evento IS NULL OR minuto_evento BETWEEN 0 AND 40", name="ck_eventos_minuto"),
    )

    partida = relationship("Partida", back_populates="eventos")
    jogador_principal = relationship("Jogador", back_populates="eventos_principal")
    zona_quadra = relationship("ZonaQuadra")


class Falta(Base):
    __tablename__ = "faltas"
    falta_id = Column(String(12), primary_key=True, default=lambda: gerar_id("FL", 6))
    partida_id = Column(String(12), ForeignKey("partidas.partida_id", onupdate="CASCADE"), nullable=False)
    jogador_id = Column(String(8), ForeignKey("jogadores.jogador_id", onupdate="CASCADE"), nullable=False)
    zona_quadra_id = Column(String(6), ForeignKey("zonas_quadra.zona_quadra_id", onupdate="CASCADE"), nullable=False)
    tipo_falta = Column(Enum("sofrida", "cometida", name="tipo_falta_enum"), nullable=False)
    gerou_cartao = Column(Boolean, nullable=False, default=False)
    periodo = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("periodo IN (1,2)", name="ck_faltas_periodo"),
    )

    partida = relationship("Partida", back_populates="faltas")


class Finalizacao(Base):
    __tablename__ = "finalizacoes"
    finalizacao_id = Column(String(12), primary_key=True, default=lambda: gerar_id("FN", 6))
    partida_id = Column(String(12), ForeignKey("partidas.partida_id", onupdate="CASCADE"), nullable=False)
    jogador_id = Column(String(8), ForeignKey("jogadores.jogador_id", onupdate="CASCADE"), nullable=False)
    zona_quadra_id = Column(String(6), ForeignKey("zonas_quadra.zona_quadra_id", onupdate="CASCADE"), nullable=False)
    zona_goleira_id = Column(String(6), ForeignKey("zonas_goleira.zona_goleira_id", onupdate="CASCADE"), nullable=False)
    tipo_ataque_id = Column(String(6), ForeignKey("tipos_ataque.tipo_ataque_id", onupdate="CASCADE"), nullable=False)
    periodo = Column(Integer, nullable=False)
    rebote = Column(Boolean, nullable=True, default=False)

    __table_args__ = (
        CheckConstraint("periodo IN (1,2)", name="ck_finalizacoes_periodo"),
    )

    partida = relationship("Partida", back_populates="finalizacoes")


class Assistencia(Base):
    __tablename__ = "assistencias"
    assistencia_id = Column(String(10), primary_key=True, default=lambda: gerar_id("AS", 6))
    finalizacao_id = Column(String(12), ForeignKey("finalizacoes.finalizacao_id", onupdate="CASCADE"), nullable=False)
    jogador_id = Column(String(8), ForeignKey("jogadores.jogador_id", onupdate="CASCADE"), nullable=False)
    jogador_assistido_id = Column(String(8), ForeignKey("jogadores.jogador_id", onupdate="CASCADE"), nullable=False)
    zona_quadra_id = Column(String(6), ForeignKey("zonas_quadra.zona_quadra_id", onupdate="CASCADE"), nullable=False)
    tipo_ataque_id = Column(String(6), ForeignKey("tipos_ataque.tipo_ataque_id", onupdate="CASCADE"), nullable=False)
    assistencia_convertida = Column(Boolean, nullable=False, default=False)
    periodo = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("periodo IN (1,2)", name="ck_assistencias_periodo"),
    )


class Passe(Base):
    __tablename__ = "passes"
    passe_id = Column(String(12), primary_key=True, default=lambda: gerar_id("PS", 6))
    partida_id = Column(String(12), ForeignKey("partidas.partida_id", onupdate="CASCADE"), nullable=False)
    jogador_origem_id = Column(String(8), ForeignKey("jogadores.jogador_id", onupdate="CASCADE"), nullable=False)
    zona_origem_id = Column(String(6), ForeignKey("zonas_quadra.zona_quadra_id", onupdate="CASCADE"), nullable=False)
    zona_destino_id = Column(String(6), ForeignKey("zonas_quadra.zona_quadra_id", onupdate="CASCADE"), nullable=False)
    tipo_passe = Column(Enum("rasteiro", "alto", name="tipo_passe_enum"), nullable=False)
    passe_errado = Column(Boolean, nullable=False, default=False)
    tipo_ataque_id = Column(String(6), ForeignKey("tipos_ataque.tipo_ataque_id", onupdate="CASCADE"), nullable=False)
    periodo = Column(Integer, nullable=False)
    minuto = Column(Integer, nullable=True)

    __table_args__ = (
        CheckConstraint("periodo IN (1,2)", name="ck_passes_periodo"),
        CheckConstraint("minuto IS NULL OR minuto BETWEEN 0 AND 40", name="ck_passes_minuto"),
    )

    partida = relationship("Partida", back_populates="passes")


class AcaoDefensiva(Base):
    __tablename__ = "acoes_defensivas"
    acao_defensiva_id = Column(String(12), primary_key=True, default=lambda: gerar_id("AD", 6))
    partida_id = Column(String(12), ForeignKey("partidas.partida_id", onupdate="CASCADE"), nullable=False)
    jogador_id = Column(String(8), ForeignKey("jogadores.jogador_id", onupdate="CASCADE"), nullable=False)
    zona_quadra_id = Column(String(6), ForeignKey("zonas_quadra.zona_quadra_id", onupdate="CASCADE"), nullable=False)
    tipo_acao = Column(Enum("desarme_cp", "desarme_sp", "interceptacao_cp", "interceptacao_sp", name="tipo_acao_defensiva_enum"), nullable=False)
    periodo = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("periodo IN (1,2)", name="ck_acoes_defensivas_periodo"),
    )

    partida = relationship("Partida", back_populates="acoes_defensivas")


class Lesao(Base):
    __tablename__ = "lesoes"
    lesao_id = Column(String(12), primary_key=True, default=lambda: gerar_id("LS", 6))
    jogador_id = Column(String(8), ForeignKey("jogadores.jogador_id", onupdate="CASCADE"), nullable=False)
    tipo_lesao = Column(String(100), nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_retorno_previsto = Column(Date, nullable=True)
    data_retorno_efetivo = Column(Date, nullable=True)
    descricao = Column(Text, nullable=True)
    parte_corpo = Column(Enum("tornozelo", "joelho", "coxa", "quadril", "costas", "ombro", "outro", name="parte_corpo_enum"), nullable=True)
    gravidade = Column(Enum("leve", "moderada", "grave", name="gravidade_enum"), nullable=True)
    situacao = Column(Enum("em_tratamento", "recuperado", "cronifica", name="situacao_enum"), nullable=True, default="em_tratamento")

    jogador = relationship("Jogador", back_populates="lesoes")


# ---------------------------
# FUNÇÕES DE CONEXÃO E CRIAÇÃO DO BD
# ---------------------------

def get_db():
    """
    Gera uma sessão do banco de dados e garante seu fechamento.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def criar_bd():
    """
    Cria todas as tabelas no banco de dados.
    """
    print("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")


if __name__ == "__main__":
    criar_bd()
