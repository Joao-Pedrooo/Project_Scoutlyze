# Bash de rodar uvicorn local


# uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

📁 maisanalise/
├── 📁 app/
│ ├── 📁 models/ # Modelos do SQLAlchemy
│ │ ├── **init**.py # Inicializa os modelos
│ │ ├── jogador.py # Modelo para a tabela 'Jogadores'
│ │ ├── time.py # Modelo para a tabela 'Times'
│ │ ├── partida.py # Modelo para a tabela 'Partidas'
│ │ └── outros_modelos.py # Outros modelos como Eventos, Duelos, etc.
│ │
│ ├── 📁 routers/ # Rotas do FastAPI
│ │ ├── **init**.py # Inicializa os routers
│ │ ├── jogadores.py # Rotas relacionadas aos jogadores
│ │ ├── times.py # Rotas relacionadas aos times
│ │ ├── partidas.py # Rotas para partidas
│ │ └── outros_routers.py # Rotas adicionais
│ │
│ ├── 📁 templates/ # Templates HTML (Jinja2)
│ │ ├── base.html # Layout base
│ │ ├── home.html # Página inicial
│ │ ├── jogadores.html # Página de jogadores
│ │ └── times.html # Página de times
│ │
│ ├── 📁 static/ # Arquivos estáticos (CSS, JS, imagens)
│ │ ├── css/
│ │ │ └── styles.css # Estilização personalizada
│ │ ├── images/
│ │ │ ├── logo.png # Logo do projeto
│ │ │ └── banner.jpg # Imagens utilizadas
│ │ └── js/
│ │ └── scripts.js # JavaScript personalizado
│ │
│ ├── **init**.py # Inicialização da aplicação
│ ├── database.py # Configuração do banco de dados
│ ├── main.py # Arquivo principal do FastAPI
│ └── config.py # Configurações gerais (carrega variáveis do .env)
│
├── .env # Variáveis de ambiente
├── requirements.txt # Dependências do projeto
├── venv/ # Ambiente virtual Python
└── README.md # Instruções do projeto
Arquivos principais:
app/main.py

Configura e inicializa o FastAPI.
Inclui os routers configurados.
app/database.py

Configura o banco de dados SQLite.
Cria a engine e a sessão.
app/models/

Contém os modelos para as tabelas do banco de dados.
app/routers/

Contém as rotas para diferentes funcionalidades (ex.: criar jogador, listar times).
templates/

Armazena os arquivos HTML para renderizar as páginas no navegador.
static/

Contém os arquivos CSS, imagens e scripts JS.



## Heranca de outras paginas do menu principal

{% extends "base.html" %}

{% block title %}Home{% endblock %}

{% block content %}
#html
{% endblock %}

## anota

# id jogador
 4 digitos
# id time
 3 digitos
