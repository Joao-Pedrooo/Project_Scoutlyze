import random
import string
from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    Enum,
    Boolean,
    create_engine,
    DateTime,
    func

)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Configuração do banco de dados SQLite
DATABASE_URL = "sqlite:///./futsal_analysis.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Função para gerar IDs no formato especificado
def gerar_id(prefixo, tamanho=6):
    return f"{prefixo}{''.join(random.choices(string.digits, k=tamanho))}"

# ------------------- TABELAS PRINCIPAIS -------------------

class Time(Base):
    __tablename__ = "times"
    time_id = Column(String(8), primary_key=True, default=lambda: gerar_id("TM", 6))
    nome = Column(String(100), nullable=False)
    categoria = Column(Enum("profissional", "base", "feminino", name="categoria_enum"), nullable=False)

    jogadores = relationship("Jogador", back_populates="time", cascade="all, delete-orphan")
    partidas_casa = relationship("Partida", foreign_keys="[Partida.time_casa_id]", back_populates="time_casa", cascade="all, delete-orphan")
    partidas_visitante = relationship("Partida", foreign_keys="[Partida.time_visitante_id]", back_populates="time_visitante", cascade="all, delete-orphan")

class Jogador(Base):
    __tablename__ = "jogadores"
    jogador_id = Column(String(8), primary_key=True, default=lambda: gerar_id("JG", 6))
    time_id = Column(String(8), ForeignKey("times.time_id"), nullable=False)
    nome = Column(String(100), nullable=False)
    numero_camisa = Column(String(2), nullable=False)  # (00-99)
    posicao = Column(Enum("goleiro", "fixo", "ala", "pivo", name="posicao_enum"), nullable=False)
    pe_dominante = Column(String(20), nullable=False)
    created_at = Column(DateTime, server_default=func.now())  # Nova coluna para a data de criação
    time = relationship("Time", back_populates="jogadores")
    # Eventos em que o jogador é o principal (ex.: finalizações, interceptações, etc.)
    eventos_principal = relationship("Evento", foreign_keys="[Evento.jogador_id]", back_populates="jogador_principal")
    # Eventos em que o jogador atuou como assistência
    eventos_assistencia = relationship("Evento", foreign_keys="[Evento.jogador_assistencia_id]", back_populates="jogador_assistencia")

class Partida(Base):
    __tablename__ = "partidas"
    partida_id = Column(String(12), primary_key=True, default=lambda: gerar_id("PT2024", 6))
    time_casa_id = Column(String(8), ForeignKey("times.time_id"), nullable=False)
    time_visitante_id = Column(String(8), ForeignKey("times.time_id"), nullable=False)
    campeonato = Column(String(100), nullable=False)
    fase_competicao = Column(Enum("classificatorio", "eliminatorio", name="fase_competicao_enum"), nullable=False)
    rodada = Column(Integer, nullable=True)  # obrigatório se fase for classificatorio
    local_partida = Column(Enum("Casa", "Fora", name="local_partida_enum"), nullable=True)  # obrigatório se eliminatorio
    data_partida = Column(DateTime, nullable=False)
    placar_casa = Column(Integer, default=0)
    placar_visitante = Column(Integer, default=0)
    periodo = Column(Integer, nullable=False)       # se ainda necessário, ex: 1 ou 2
    minuto_acao = Column(Integer, nullable=False)     # (0-40)
    placar_momento = Column(String(10), nullable=False) # ex: "0x0"
    created_at = Column(DateTime, default=func.now(), nullable=False)

    time_casa = relationship("Time", foreign_keys=[time_casa_id], back_populates="partidas_casa")
    time_visitante = relationship("Time", foreign_keys=[time_visitante_id], back_populates="partidas_visitante")
    eventos = relationship("Evento", back_populates="partida", cascade="all, delete-orphan")
    finalizacoes = relationship("Finalizacao", back_populates="partida", cascade="all, delete-orphan")
    acoes_defensivas = relationship("AcaoDefensiva", back_populates="partida", cascade="all, delete-orphan")
    faltas = relationship("Falta", back_populates="partida", cascade="all, delete-orphan")
    escanteios = relationship("Escanteio", back_populates="partida", cascade="all, delete-orphan")
    substituicoes = relationship("Substituicao", back_populates="partida", cascade="all, delete-orphan")
    momentos = relationship("MomentoDoJogo", back_populates="partida", cascade="all, delete-orphan")

# ------------------- TABELAS DE ZONAS E TIPOS -------------------

class ZonaQuadra(Base):
    __tablename__ = "zonas_quadra"
    zona_quadra_id = Column(String(6), primary_key=True, default=lambda: gerar_id("ZQ", 4))
    numero_zona = Column(Integer, nullable=False)  # (1-12)

    eventos = relationship("Evento", back_populates="zona_quadra", cascade="all, delete-orphan")
    finalizacoes = relationship("Finalizacao", back_populates="zona_quadra", cascade="all, delete-orphan")
    assistencias = relationship("Assistencia", back_populates="zona_quadra", cascade="all, delete-orphan")
    acoes_defensivas = relationship("AcaoDefensiva", back_populates="zona_quadra", cascade="all, delete-orphan")
    faltas = relationship("Falta", back_populates="zona_quadra", cascade="all, delete-orphan")

class ZonaGoleira(Base):
    __tablename__ = "zonas_goleira"
    zona_goleira_id = Column(String(6), primary_key=True, default=lambda: gerar_id("ZG", 4))
    numero_zona_goleira = Column(Integer, nullable=False)  # (1-16)

    finalizacoes = relationship("Finalizacao", back_populates="zona_goleira", cascade="all, delete-orphan")

class TipoAtaque(Base):
    __tablename__ = "tipos_ataque"
    tipo_ataque_id = Column(String(6), primary_key=True, default=lambda: gerar_id("TA", 4))
    nome = Column(Enum("ataque_posicional", "ataque_rapido", "contra_ataque", "lateral", "falta", "tiro_livre", "penalti", "escanteio", "5x4", "goleiro_linha", name="tipo_ataque_enum"), nullable=False)
    descricao_vantagem = Column(Enum("vantagem_numerica", "desvantagem_numerica", "equidade_numerica", name="descricao_vantagem_enum"), nullable=False)
    periodo = Column(Integer, nullable=False)  # (1 ou 2)

    finalizacoes = relationship("Finalizacao", back_populates="tipo_ataque", cascade="all, delete-orphan")
    assistencias = relationship("Assistencia", back_populates="tipo_ataque", cascade="all, delete-orphan")

# ------------------- TABELAS DE EVENTOS E AÇÕES -------------------

class Evento(Base):
    __tablename__ = "eventos"
    evento_id = Column(String(12), primary_key=True, default=lambda: gerar_id("EV2024", 6))
    partida_id = Column(String(12), ForeignKey("partidas.partida_id"), nullable=False)
    jogador_id = Column(String(8), ForeignKey("jogadores.jogador_id"), nullable=False)  # Jogador principal
    jogador_assistencia_id = Column(String(8), ForeignKey("jogadores.jogador_id"), nullable=True)  # Jogador que assistiu
    tipo_evento = Column(Enum("defesa", "passe", "interceptacao", "desarme", "finalizacao", name="tipo_evento_enum"), nullable=False)
    subtipo_evento = Column(Enum("defesa_pe", "defesa_mao", "passe_rasteiro", "passe_alto", "outro", name="subtipo_evento_enum"), nullable=False)
    parte_corpo = Column(Enum("pe_direito", "pe_esquerdo", "cabeca", "peito", "mao", name="parte_corpo_enum"), nullable=False)
    zona_quadra_id = Column(String(6), ForeignKey("zonas_quadra.zona_quadra_id"), nullable=False)
    periodo = Column(Integer, nullable=False)
    minuto_evento = Column(Integer, nullable=False)
    situacao_jogo = Column(Enum("regular", "powerplay", "inferioridade", name="situacao_jogo_enum"), nullable=False)

    partida = relationship("Partida", back_populates="eventos")
    jogador_principal = relationship("Jogador", foreign_keys=[jogador_id], back_populates="eventos_principal")
    jogador_assistencia = relationship("Jogador", foreign_keys=[jogador_assistencia_id], back_populates="eventos_assistencia")
    zona_quadra = relationship("ZonaQuadra", back_populates="eventos")

class Finalizacao(Base):
    __tablename__ = "finalizacoes"
    finalizacao_id = Column(String(12), primary_key=True, default=lambda: gerar_id("FN2024", 6))
    partida_id = Column(String(12), ForeignKey("partidas.partida_id"), nullable=False)
    jogador_id = Column(String(8), ForeignKey("jogadores.jogador_id"), nullable=False)  # Jogador finalizador
    zona_quadra_id = Column(String(6), ForeignKey("zonas_quadra.zona_quadra_id"), nullable=False)
    zona_goleira_id = Column(String(6), ForeignKey("zonas_goleira.zona_goleira_id"), nullable=False)
    tipo_ataque_id = Column(String(6), ForeignKey("tipos_ataque.tipo_ataque_id"), nullable=False)
    tipo_finalizacao = Column(Enum("chute_rasteiro", "chute_alto", "cabecada", "toque", name="tipo_finalizacao_enum"), nullable=False)
    resultado = Column(Enum("gol", "trave", "fora", "defesa_goleiro", "bloqueado", name="resultado_enum"), nullable=False)
    periodo = Column(Integer, nullable=False)

    partida = relationship("Partida", back_populates="finalizacoes")
    zona_quadra = relationship("ZonaQuadra", back_populates="finalizacoes")
    zona_goleira = relationship("ZonaGoleira", back_populates="finalizacoes")
    tipo_ataque = relationship("TipoAtaque", back_populates="finalizacoes")
    assistencias = relationship("Assistencia", back_populates="finalizacao", cascade="all, delete-orphan")

class Assistencia(Base):
    __tablename__ = "assistencias"
    assistencia_id = Column(String(10), primary_key=True, default=lambda: gerar_id("AS", 6))
    finalizacao_id = Column(String(12), ForeignKey("finalizacoes.finalizacao_id"), nullable=False)
    jogador_id = Column(String(8), ForeignKey("jogadores.jogador_id"), nullable=False)  # Jogador que assistiu
    jogador_assistido_id = Column(String(8), ForeignKey("jogadores.jogador_id"), nullable=False)  # Jogador que recebeu
    zona_quadra_id = Column(String(6), ForeignKey("zonas_quadra.zona_quadra_id"), nullable=False)
    tipo_ataque_id = Column(String(6), ForeignKey("tipos_ataque.tipo_ataque_id"), nullable=False)
    assistencia_convertida = Column(Boolean, nullable=False)
    periodo = Column(Integer, nullable=False)

    finalizacao = relationship("Finalizacao", back_populates="assistencias")
    zona_quadra = relationship("ZonaQuadra", back_populates="assistencias")
    tipo_ataque = relationship("TipoAtaque", back_populates="assistencias")

class AcaoDefensiva(Base):
    __tablename__ = "acoes_defensivas"
    acao_defensiva_id = Column(String(12), primary_key=True, default=lambda: gerar_id("AD2024", 6))
    partida_id = Column(String(12), ForeignKey("partidas.partida_id"), nullable=False)
    jogador_id = Column(String(8), ForeignKey("jogadores.jogador_id"), nullable=False)
    zona_quadra_id = Column(String(6), ForeignKey("zonas_quadra.zona_quadra_id"), nullable=False)
    tipo_acao = Column(Enum("bloqueio", "interceptacao", "desarme", "antecipacao", name="tipo_acao_enum"), nullable=False)
    periodo = Column(Integer, nullable=False)

    partida = relationship("Partida", back_populates="acoes_defensivas")
    zona_quadra = relationship("ZonaQuadra", back_populates="acoes_defensivas")

# ------------------- TABELAS COMPLEMENTARES -------------------

class Falta(Base):
    __tablename__ = "faltas"
    falta_id = Column(String(12), primary_key=True, default=lambda: gerar_id("FL2024", 6))
    partida_id = Column(String(12), ForeignKey("partidas.partida_id"), nullable=False)
    jogador_id = Column(String(8), ForeignKey("jogadores.jogador_id"), nullable=False)
    zona_quadra_id = Column(String(6), ForeignKey("zonas_quadra.zona_quadra_id"), nullable=False)
    tipo_falta = Column(Enum("sofrida", "cometida", name="tipo_falta_enum"), nullable=False)
    gerou_cartao = Column(Boolean, nullable=False)
    periodo = Column(Integer, nullable=False)

    partida = relationship("Partida", back_populates="faltas")
    zona_quadra = relationship("ZonaQuadra", back_populates="faltas")

class Escanteio(Base):
    __tablename__ = "escanteios"
    escanteio_id = Column(String(12), primary_key=True, default=lambda: gerar_id("EC2024", 6))
    partida_id = Column(String(12), ForeignKey("partidas.partida_id"), nullable=False)
    escanteios_pro = Column(Integer, nullable=False)
    escanteios_contra = Column(Integer, nullable=False)
    periodo = Column(Integer, nullable=False)

    partida = relationship("Partida", back_populates="escanteios")

class Substituicao(Base):
    __tablename__ = "substituicoes"
    substituicao_id = Column(String(12), primary_key=True, default=lambda: gerar_id("SB2024", 6))
    partida_id = Column(String(12), ForeignKey("partidas.partida_id"), nullable=False)
    jogador_saiu_id = Column(String(8), ForeignKey("jogadores.jogador_id"), nullable=False)
    jogador_entrou_id = Column(String(8), ForeignKey("jogadores.jogador_id"), nullable=False)
    minuto = Column(Integer, nullable=False)
    periodo = Column(Integer, nullable=False)

    partida = relationship("Partida", back_populates="substituicoes")

class MomentoDoJogo(Base):
    __tablename__ = "momentos_do_jogo"
    momento_id = Column(String(12), primary_key=True, default=lambda: gerar_id("MJ2024", 6))
    partida_id = Column(String(12), ForeignKey("partidas.partida_id"), nullable=False)
    tipo_momento = Column(Enum("timeout", "powerplay_inicio", "powerplay_fim", "cartao", name="tipo_momento_enum"), nullable=False)
    minuto = Column(Integer, nullable=False)
    periodo = Column(Integer, nullable=False)

    partida = relationship("Partida", back_populates="momentos")

# ------------------- FUNÇÃO GET_DB -------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------- FUNÇÃO PARA CRIAR O BANCO -------------------
def criar_bd():
    print("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    criar_bd()

criar_bd()