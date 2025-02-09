{% extends "base.html" %}

{% block title %}Jogo ao Vivo - {{ partida.time_casa.nome }} vs {{ partida.time_visitante.nome }}{% endblock %}

{% block content %}
<div class="container mt-4">
    <!-- Scoreboard no Topo -->
    <div class="row text-center mb-4">
        <div class="col-md-6">
            <div class="card bg-light border-primary">
                <div class="card-body">
                    <h4 class="card-title">Gol</h4>
                    <h2>{{ partida.placar_casa }}</h2>
                    <p>{{ partida.time_casa.nome }}</p>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card bg-light border-danger">
                <div class="card-body">
                    <h4 class="card-title">Gol Adversário</h4>
                    <h2>{{ partida.placar_visitante }}</h2>
                    <p>{{ partida.time_visitante.nome }}</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Abas para separar o Registro de Evento e os Dados do Gol -->
    <ul class="nav nav-tabs" id="tabEventoGol" role="tablist">
        <li class="nav-item" role="presentation">
            <button class="nav-link active" id="evento-tab" data-bs-toggle="tab" data-bs-target="#evento" type="button" role="tab" aria-controls="evento" aria-selected="true">
                Registrar Evento
            </button>
        </li>
        <li class="nav-item" role="presentation">
            <button class="nav-link" id="gol-tab" data-bs-toggle="tab" data-bs-target="#gol" type="button" role="tab" aria-controls="gol" aria-selected="false">
                Dados do Gol
            </button>
        </li>
    </ul>
    <div class="tab-content pt-3" id="tabEventoGolContent">
        <!-- Aba: Registrar Evento -->
        <div class="tab-pane fade show active" id="evento" role="tabpanel" aria-labelledby="evento-tab">
            <!-- Formulário para Registrar Evento -->
    <h3 class="text-center">Registrar Evento</h3>
    <form action="/api/jogo_ao_vivo/{{ partida.partida_id }}/evento" method="post" id="eventoForm" class="mb-4">
        <div class="mb-3">
            <label for="categoria_evento" class="form-label">Categoria do Evento</label>
            <select id="categoria_evento" name="categoria_evento" class="form-select" required onchange="mostrarGrupo(this.value)">
                <option value="" disabled selected>Selecione a categoria do evento</option>
                <option value="evento">Evento</option>
                <option value="finalizacao">Finalização</option>
                <option value="assistencia">Assistência</option>
                <option value="acao_defensiva">Ação Defensiva</option>
            </select>
        </div>

        <!-- Grupo para Evento -->
        <div id="grupo_evento" style="display:none;">
            <h4>Evento</h4>
            <div class="mb-3">
                <label for="jogador_id_evento" class="form-label">Número do Jogador</label>
                <select id="jogador_id_evento" name="jogador_id" class="form-select" required>
                    <option value="" disabled selected>Selecione o jogador (por número)</option>
                    {% for jogador in jogadores %}
                    <option value="{{ jogador.jogador_id }}">{{ jogador.numero_camisa }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="subtipo_evento" class="form-label">Subtipo do Evento</label>
                <select id="subtipo_evento" name="subtipo_evento" class="form-select">
                    <option value="" disabled selected>Selecione o subtipo</option>
                    {% for sub in subtipos_evento %}
                    <option value="{{ sub }}">{{ sub|replace("_", " ")|capitalize }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="parte_corpo" class="form-label">Parte do Corpo</label>
                <select id="parte_corpo" name="parte_corpo" class="form-select" required>
                    <option value="" disabled selected>Selecione a parte do corpo</option>
                    {% for parte in partes_corpo %}
                    <option value="{{ parte }}">{{ parte|replace("_", " ")|capitalize }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="zona_quadra_evento" class="form-label">Zona da Quadra</label>
                <select id="zona_quadra_evento" name="zona_quadra" class="form-select" required>
                    <option value="" disabled selected>Selecione a zona da quadra</option>
                    {% for zona in zonas_quadra %}
                    <option value="{{ zona }}">Zona {{ zona }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="periodo_evento" class="form-label">Período</label>
                <select id="periodo_evento" name="periodo" class="form-select" required>
                    <option value="" disabled selected>Selecione o período</option>
                    <option value="1">1º Período</option>
                    <option value="2">2º Período</option>
                </select>
            </div>
            <div class="mb-3">
                <label for="minuto_evento" class="form-label">Minuto do Evento</label>
                <input type="number" id="minuto_evento" name="minuto_evento" class="form-control" required min="0" max="40" />
            </div>
            <div class="mb-3">
                <label for="situacao_jogo" class="form-label">Situação do Jogo</label>
                <select id="situacao_jogo" name="situacao_jogo" class="form-select" required>
                    <option value="" disabled selected>Selecione a situação</option>
                    {% for situacao in situacoes_jogo %}
                    <option value="{{ situacao }}">{{ situacao|capitalize }}</option>
                    {% endfor %}
                </select>
            </div>
        </div>

        <!-- Grupo para Finalização -->
        <div id="grupo_finalizacao" style="display:none;">
            <h4>Finalização</h4>
            <div class="mb-3">
                <label for="jogador_id_finalizacao" class="form-label">Número do Jogador Finalizador</label>
                <select id="jogador_id_finalizacao" name="jogador_id" class="form-select" required>
                    <option value="" disabled selected>Selecione o jogador (por número)</option>
                    {% for jogador in jogadores %}
                    <option value="{{ jogador.jogador_id }}">{{ jogador.numero_camisa }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="zona_quadra_finalizacao" class="form-label">Zona da Quadra de Finalização</label>
                <select id="zona_quadra_finalizacao" name="zona_quadra" class="form-select" required>
                    <option value="" disabled selected>Selecione a zona da quadra</option>
                    {% for zona in zonas_quadra %}
                    <option value="{{ zona }}">Zona {{ zona }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="zona_goleira_finalizacao" class="form-label">Zona do Gol</label>
                <select id="zona_goleira_finalizacao" name="zona_goleira" class="form-select" required>
                    <option value="" disabled selected>Selecione a zona do gol</option>
                    {% for zona in zonas_goleira %}
                    <option value="{{ zona }}">Zona {{ zona }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="tipo_ataque_finalizacao" class="form-label">Tipo de Gol</label>
                <select id="tipo_ataque_finalizacao" name="tipo_ataque" class="form-select" required>
                    <option value="" disabled selected>Selecione o tipo de gol</option>
                    {% for tipo in tipos_gol %}
                    <option value="{{ tipo }}">{{ tipo|replace("_", " ")|capitalize }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="tipo_finalizacao" class="form-label">Tipo de Finalização</label>
                <select id="tipo_finalizacao" name="tipo_finalizacao" class="form-select" required>
                    <option value="" disabled selected>Selecione o tipo de finalização</option>
                    <option value="chute_rasteiro">Chute Rasteiro</option>
                    <option value="chute_alto">Chute Alto</option>
                    <option value="cabecada">Cabecada</option>
                    <option value="toque">Toque</option>
                </select>
            </div>
            <div class="mb-3">
                <label for="resultado_finalizacao" class="form-label">Resultado</label>
                <select id="resultado_finalizacao" name="resultado" class="form-select" required>
                    <option value="" disabled selected>Selecione o resultado</option>
                    <option value="gol">Gol</option>
                    <option value="trave">Trave</option>
                    <option value="fora">Fora</option>
                    <option value="defesa_goleiro">Defesa do Goleiro</option>
                    <option value="bloqueado">Bloqueado</option>
                </select>
            </div>
            <div class="mb-3">
                <label for="periodo_finalizacao" class="form-label">Período</label>
                <select id="periodo_finalizacao" name="periodo" class="form-select" required>
                    <option value="" disabled selected>Selecione o período</option>
                    <option value="1">1º Período</option>
                    <option value="2">2º Período</option>
                </select>
            </div>
        </div>

        <!-- Grupo para Assistência -->
        <div id="grupo_assistencia" style="display:none;">
            <h4>Assistência</h4>
            <div class="mb-3">
                <label for="finalizacao_id_assistencia" class="form-label">ID da Finalização</label>
                <input type="text" id="finalizacao_id_assistencia" name="finalizacao_id" class="form-control" placeholder="Digite o ID da finalização" required />
            </div>
            <div class="mb-3">
                <label for="jogador_id_assistencia" class="form-label">Número do Jogador que Assistiu</label>
                <select id="jogador_id_assistencia" name="jogador_id" class="form-select" required>
                    <option value="" disabled selected>Selecione o jogador (por número)</option>
                    {% for jogador in jogadores %}
                    <option value="{{ jogador.jogador_id }}">{{ jogador.numero_camisa }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="jogador_assistido_id" class="form-label">Número do Jogador Assistido</label>
                <select id="jogador_assistido_id" name="jogador_assistido_id" class="form-select" required>
                    <option value="" disabled selected>Selecione o jogador (por número)</option>
                    {% for jogador in jogadores %}
                    <option value="{{ jogador.jogador_id }}">{{ jogador.numero_camisa }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="zona_quadra_assistencia" class="form-label">Zona da Quadra (Assistência)</label>
                <select id="zona_quadra_assistencia" name="zona_quadra" class="form-select" required>
                    <option value="" disabled selected>Selecione a zona da quadra</option>
                    {% for zona in zonas_quadra %}
                    <option value="{{ zona }}">Zona {{ zona }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="tipo_ataque_assistencia" class="form-label">Tipo de Gol (Assistência)</label>
                <select id="tipo_ataque_assistencia" name="tipo_ataque" class="form-select" required>
                    <option value="" disabled selected>Selecione o tipo de gol</option>
                    {% for tipo in tipos_gol %}
                    <option value="{{ tipo }}">{{ tipo|replace("_", " ")|capitalize }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="assistencia_convertida" class="form-label">Assistência Convertida</label>
                <select id="assistencia_convertida" name="assistencia_convertida" class="form-select" required>
                    <option value="" disabled selected>Selecione</option>
                    <option value="true">Sim</option>
                    <option value="false">Não</option>
                </select>
            </div>
            <div class="mb-3">
                <label for="periodo_assistencia" class="form-label">Período</label>
                <select id="periodo_assistencia" name="periodo" class="form-select" required>
                    <option value="" disabled selected>Selecione o período</option>
                    <option value="1">1º Período</option>
                    <option value="2">2º Período</option>
                </select>
            </div>
        </div>

        <!-- Grupo para Ação Defensiva -->
        <div id="grupo_acao_defensiva" style="display:none;">
            <h4>Ação Defensiva</h4>
            <div class="mb-3">
                <label for="jogador_id_defensiva" class="form-label">Número do Jogador</label>
                <select id="jogador_id_defensiva" name="jogador_id" class="form-select" required>
                    <option value="" disabled selected>Selecione o jogador (por número)</option>
                    {% for jogador in jogadores %}
                    <option value="{{ jogador.jogador_id }}">{{ jogador.numero_camisa }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="zona_quadra_defensiva" class="form-label">Zona da Quadra</label>
                <select id="zona_quadra_defensiva" name="zona_quadra" class="form-select" required>
                    <option value="" disabled selected>Selecione a zona da quadra</option>
                    {% for zona in zonas_quadra %}
                    <option value="{{ zona }}">Zona {{ zona }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="tipo_acao" class="form-label">Tipo de Ação</label>
                <select id="tipo_acao" name="tipo_acao" class="form-select" required>
                    <option value="" disabled selected>Selecione a ação defensiva</option>
                    {% for acao in tipos_acao_defensiva %}
                    <option value="{{ acao }}">{{ acao|capitalize }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="periodo_defensiva" class="form-label">Período</label>
                <select id="periodo_defensiva" name="periodo" class="form-select" required>
                    <option value="" disabled selected>Selecione o período</option>
                    <option value="1">1º Período</option>
                    <option value="2">2º Período</option>
                </select>
            </div>
        </div>

        <button type="submit" class="btn btn-success w-100">
            <i class="fas fa-check"></i> Registrar Evento
        </button>
    </form>

    <!-- Lista de Eventos Registrados -->
    <h2 class="text-center mt-5">Eventos Registrados</h2>
    <div class="list-group">
        {% for evento in eventos %}
        <div class="list-group-item">
            <strong>{{ evento.tipo_evento|capitalize }}</strong>
            {% if evento.subtipo_evento %} - {{ evento.subtipo_evento|replace("_", " ")|capitalize }}{% endif %}
            {% if evento.parte_corpo %} - {{ evento.parte_corpo|replace("_", " ")|capitalize }}{% endif %}
            {% if evento.zona_quadra_id %} - Zona Quadra: {{ evento.zona_quadra_id }}{% endif %}
            {% if evento.periodo %} - Período: {{ evento.periodo }}{% endif %}
            {% if evento.minuto_evento %} - Minuto: {{ evento.minuto_evento }}{% endif %}
            {% if evento.situacao_jogo %} - Situação: {{ evento.situacao_jogo|capitalize }}{% endif %}
        </div>
        {% else %}
        <div class="list-group-item text-center">
            Nenhum evento registrado.
        </div>
        {% endfor %}
    </div>

    <!-- Botão para Encerrar o Jogo Ao Vivo -->
    <form action="/api/jogo_ao_vivo/{{ partida.partida_id }}/encerrar" method="post" class="mt-4">
        <button type="submit" class="btn btn-danger w-100">
            <i class="fas fa-stop"></i> Encerrar Jogo
        </button>
    </form>
</div>
        </div>

        <!-- Aba: Dados do Gol -->
        <div class="tab-pane fade" id="gol" role="tabpanel" aria-labelledby="gol-tab">
            <h4 class="mb-3">Dados do Gol</h4>
            <form action="/api/jogo_ao_vivo/{{ partida.partida_id }}/evento" method="post" id="finalizacaoForm">
                <!-- Categoria definida como finalizacao -->
                <input type="hidden" name="categoria_evento" value="finalizacao">

                <!-- Seleção do Time que Marcou -->
                <div class="mb-3">
                    <label class="form-label">Time que Marcou</label><br>
                    <div class="form-check form-check-inline">
                        <input class="form-check-input" type="radio" name="time_marcador" id="radio_meu" value="meu" onclick="mostrarJogador('meu')" required>
                        <label class="form-check-label" for="radio_meu">Meu Time</label>
                    </div>
                    <div class="form-check form-check-inline">
                        <input class="form-check-input" type="radio" name="time_marcador" id="radio_adv" value="adversario" onclick="mostrarJogador('adversario')">
                        <label class="form-check-label" for="radio_adv">Time Adversário</label>
                    </div>
                </div>

                <!-- Dropdown para jogador do Meu Time -->
                <div class="mb-3" id="div_jogador_meu" style="display:none;">
                    <label for="jogador_meu" class="form-label">Número do Jogador (Meu Time)</label>
                    <select id="jogador_meu" name="jogador_id" class="form-select">
                        <option value="" disabled selected>Selecione o jogador</option>
                        {% for jogador in jogadores_meu %}
                        <option value="{{ jogador.jogador_id }}">{{ jogador.numero_camisa }}</option>
                        {% endfor %}
                    </select>
                </div>

                <!-- Dropdown para jogador do Time Adversário -->
                <div class="mb-3" id="div_jogador_adv" style="display:none;">
                    <label for="jogador_adv" class="form-label">Número do Jogador (Time Adversário)</label>
                    <select id="jogador_adv" name="jogador_id" class="form-select">
                        <option value="" disabled selected>Selecione o jogador</option>
                        {% for jogador in jogadores_adv %}
                        <option value="{{ jogador.jogador_id }}">{{ jogador.numero_camisa }}</option>
                        {% endfor %}
                    </select>
                </div>

                <!-- Dropdown para Zona da Quadra (12 zonas) -->
                <div class="mb-3">
                    <label for="zona_quadra_finalizacao" class="form-label">Zona da Quadra</label>
                    <select id="zona_quadra_finalizacao" name="zona_quadra" class="form-select" required>
                        <option value="" disabled selected>Selecione a zona da quadra</option>
                        {% for zona in zonas_quadra %}
                        <option value="{{ zona }}">Zona {{ zona }}</option>
                        {% endfor %}
                    </select>
                </div>

                <!-- Dropdown para Zona do Gol (16 zonas) -->
                <div class="mb-3">
                    <label for="zona_goleira_finalizacao" class="form-label">Zona do Gol</label>
                    <select id="zona_goleira_finalizacao" name="zona_goleira" class="form-select" required>
                        <option value="" disabled selected>Selecione a zona do gol</option>
                        {% for zona in zonas_goleira %}
                        <option value="{{ zona }}">Zona {{ zona }}</option>
                        {% endfor %}
                    </select>
                </div>

                <!-- Dropdown para Tipo de Finalização -->
                <div class="mb-3">
                    <label for="tipo_gol_finalizacao" class="form-label">Tipo de Finalização</label>
                    <select id="tipo_gol_finalizacao" name="tipo_gol" class="form-select" required>
                        <option value="" disabled selected>Selecione o tipo de finalização</option>
                        {% for tipo in tipos_finalizacao %}
                        <option value="{{ tipo }}">{{ tipo|replace("_", " ")|capitalize }}</option>
                        {% endfor %}
                    </select>
                </div>

                <button type="submit" class="btn btn-success w-100">
                    <i class="fas fa-check"></i> Registrar Gol
                </button>
            </form>
        </div>
    </div>

    <!-- Lista de Eventos Registrados -->
    <h2 class="text-center mt-5">Eventos Registrados</h2>
    <div class="list-group">
        {% for evento in eventos %}
        <div class="list-group-item">
            <strong>{{ evento.tipo_evento|capitalize }}</strong>
            {% if evento.subtipo_evento %} - {{ evento.subtipo_evento|replace("_", " ")|capitalize }}{% endif %}
            {% if evento.parte_corpo %} - {{ evento.parte_corpo|replace("_", " ")|capitalize }}{% endif %}
            {% if evento.zona_quadra_id %} - Zona Quadra: {{ evento.zona_quadra_id }}{% endif %}
            {% if evento.periodo %} - Período: {{ evento.periodo }}{% endif %}
            {% if evento.minuto_evento %} - Minuto: {{ evento.minuto_evento }}{% endif %}
            {% if evento.situacao_jogo %} - Situação: {{ evento.situacao_jogo|capitalize }}{% endif %}
        </div>
        {% else %}
        <div class="list-group-item text-center">
            Nenhum evento registrado.
        </div>
        {% endfor %}
    </div>

    <!-- Botão para Encerrar o Jogo Ao Vivo -->
    <form action="/api/jogo_ao_vivo/{{ partida.partida_id }}/encerrar" method="post" class="mt-4">
        <button type="submit" class="btn btn-danger w-100">
            <i class="fas fa-stop"></i> Encerrar Jogo
        </button>
    </form>
</div>

<script>
    // Função para exibir o dropdown de jogador conforme o time selecionado
    function mostrarJogador(timeMarcador) {
        if(timeMarcador === "meu") {
            document.getElementById("div_jogador_meu").style.display = "block";
            document.getElementById("div_jogador_adv").style.display = "none";
        } else if(timeMarcador === "adversario") {
            document.getElementById("div_jogador_meu").style.display = "none";
            document.getElementById("div_jogador_adv").style.display = "block";
        }
    }
</script>

<!-- Bootstrap JS para as abas -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://kit.fontawesome.com/your-fontawesome-kit.js" crossorigin="anonymous"></script>
{% endblock %}





###########################################################################################################################







##############
##
##













{% extends "base.html" %}

{% block title %}Jogo ao Vivo - {{ partida.time_casa.nome }} vs {{ partida.time_visitante.nome }}{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1 class="text-center">Jogo ao Vivo: {{ partida.time_casa.nome }} vs {{ partida.time_visitante.nome }}</h1>

    <!-- Placar -->
    <div class="text-center mb-4">
        <h2>{{ partida.placar_casa }} - {{ partida.placar_visitante }}</h2>
    </div>

      <!-- Formulário para Registrar Evento -->
    <h3 class="text-center">Registrar Evento</h3>
    <form action="/api/jogo_ao_vivo/{{ partida.partida_id }}/evento" method="post" id="eventoForm" class="mb-4">
        <div class="mb-3">
            <label for="categoria_evento" class="form-label">Categoria do Evento</label>
            <select id="categoria_evento" name="categoria_evento" class="form-select" required onchange="mostrarGrupo(this.value)">
                <option value="" disabled selected>Selecione a categoria do evento</option>
                <option value="evento">Evento</option>
                <option value="finalizacao">Finalização</option>
                <option value="assistencia">Assistência</option>
                <option value="acao_defensiva">Ação Defensiva</option>
            </select>
        </div>

        <!-- Grupo para Evento -->
        <div id="grupo_evento" style="display:none;">
            <h4>Evento</h4>
            <div class="mb-3">
                <label for="jogador_id_evento" class="form-label">Número do Jogador</label>
                <select id="jogador_id_evento" name="jogador_id" class="form-select" required>
                    <option value="" disabled selected>Selecione o jogador (por número)</option>
                    {% for jogador in jogadores %}
                    <option value="{{ jogador.jogador_id }}">{{ jogador.numero_camisa }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="subtipo_evento" class="form-label">Subtipo do Evento</label>
                <select id="subtipo_evento" name="subtipo_evento" class="form-select">
                    <option value="" disabled selected>Selecione o subtipo</option>
                    {% for sub in subtipos_evento %}
                    <option value="{{ sub }}">{{ sub|replace("_", " ")|capitalize }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="parte_corpo" class="form-label">Parte do Corpo</label>
                <select id="parte_corpo" name="parte_corpo" class="form-select" required>
                    <option value="" disabled selected>Selecione a parte do corpo</option>
                    {% for parte in partes_corpo %}
                    <option value="{{ parte }}">{{ parte|replace("_", " ")|capitalize }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="zona_quadra_evento" class="form-label">Zona da Quadra</label>
                <select id="zona_quadra_evento" name="zona_quadra" class="form-select" required>
                    <option value="" disabled selected>Selecione a zona da quadra</option>
                    {% for zona in zonas_quadra %}
                    <option value="{{ zona }}">Zona {{ zona }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="periodo_evento" class="form-label">Período</label>
                <select id="periodo_evento" name="periodo" class="form-select" required>
                    <option value="" disabled selected>Selecione o período</option>
                    <option value="1">1º Período</option>
                    <option value="2">2º Período</option>
                </select>
            </div>
            <div class="mb-3">
                <label for="minuto_evento" class="form-label">Minuto do Evento</label>
                <input type="number" id="minuto_evento" name="minuto_evento" class="form-control" required min="0" max="40" />
            </div>
            <div class="mb-3">
                <label for="situacao_jogo" class="form-label">Situação do Jogo</label>
                <select id="situacao_jogo" name="situacao_jogo" class="form-select" required>
                    <option value="" disabled selected>Selecione a situação</option>
                    {% for situacao in situacoes_jogo %}
                    <option value="{{ situacao }}">{{ situacao|capitalize }}</option>
                    {% endfor %}
                </select>
            </div>
        </div>

        <!-- Grupo para Finalização -->
        <div id="grupo_finalizacao" style="display:none;">
            <h4>Finalização</h4>
            <div class="mb-3">
                <label for="jogador_id_finalizacao" class="form-label">Número do Jogador Finalizador</label>
                <select id="jogador_id_finalizacao" name="jogador_id" class="form-select" required>
                    <option value="" disabled selected>Selecione o jogador (por número)</option>
                    {% for jogador in jogadores %}
                    <option value="{{ jogador.jogador_id }}">{{ jogador.numero_camisa }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="zona_quadra_finalizacao" class="form-label">Zona da Quadra de Finalização</label>
                <select id="zona_quadra_finalizacao" name="zona_quadra" class="form-select" required>
                    <option value="" disabled selected>Selecione a zona da quadra</option>
                    {% for zona in zonas_quadra %}
                    <option value="{{ zona }}">Zona {{ zona }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="zona_goleira_finalizacao" class="form-label">Zona do Gol</label>
                <select id="zona_goleira_finalizacao" name="zona_goleira" class="form-select" required>
                    <option value="" disabled selected>Selecione a zona do gol</option>
                    {% for zona in zonas_goleira %}
                    <option value="{{ zona }}">Zona {{ zona }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="tipo_ataque_finalizacao" class="form-label">Tipo de Gol</label>
                <select id="tipo_ataque_finalizacao" name="tipo_ataque" class="form-select" required>
                    <option value="" disabled selected>Selecione o tipo de gol</option>
                    {% for tipo in tipos_gol %}
                    <option value="{{ tipo }}">{{ tipo|replace("_", " ")|capitalize }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="tipo_finalizacao" class="form-label">Tipo de Finalização</label>
                <select id="tipo_finalizacao" name="tipo_finalizacao" class="form-select" required>
                    <option value="" disabled selected>Selecione o tipo de finalização</option>
                    <option value="chute_rasteiro">Chute Rasteiro</option>
                    <option value="chute_alto">Chute Alto</option>
                    <option value="cabecada">Cabecada</option>
                    <option value="toque">Toque</option>
                </select>
            </div>
            <div class="mb-3">
                <label for="resultado_finalizacao" class="form-label">Resultado</label>
                <select id="resultado_finalizacao" name="resultado" class="form-select" required>
                    <option value="" disabled selected>Selecione o resultado</option>
                    <option value="gol">Gol</option>
                    <option value="trave">Trave</option>
                    <option value="fora">Fora</option>
                    <option value="defesa_goleiro">Defesa do Goleiro</option>
                    <option value="bloqueado">Bloqueado</option>
                </select>
            </div>
            <div class="mb-3">
                <label for="periodo_finalizacao" class="form-label">Período</label>
                <select id="periodo_finalizacao" name="periodo" class="form-select" required>
                    <option value="" disabled selected>Selecione o período</option>
                    <option value="1">1º Período</option>
                    <option value="2">2º Período</option>
                </select>
            </div>
        </div>

        <!-- Grupo para Assistência -->
        <div id="grupo_assistencia" style="display:none;">
            <h4>Assistência</h4>
            <div class="mb-3">
                <label for="finalizacao_id_assistencia" class="form-label">ID da Finalização</label>
                <input type="text" id="finalizacao_id_assistencia" name="finalizacao_id" class="form-control" placeholder="Digite o ID da finalização" required />
            </div>
            <div class="mb-3">
                <label for="jogador_id_assistencia" class="form-label">Número do Jogador que Assistiu</label>
                <select id="jogador_id_assistencia" name="jogador_id" class="form-select" required>
                    <option value="" disabled selected>Selecione o jogador (por número)</option>
                    {% for jogador in jogadores %}
                    <option value="{{ jogador.jogador_id }}">{{ jogador.numero_camisa }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="jogador_assistido_id" class="form-label">Número do Jogador Assistido</label>
                <select id="jogador_assistido_id" name="jogador_assistido_id" class="form-select" required>
                    <option value="" disabled selected>Selecione o jogador (por número)</option>
                    {% for jogador in jogadores %}
                    <option value="{{ jogador.jogador_id }}">{{ jogador.numero_camisa }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="zona_quadra_assistencia" class="form-label">Zona da Quadra (Assistência)</label>
                <select id="zona_quadra_assistencia" name="zona_quadra" class="form-select" required>
                    <option value="" disabled selected>Selecione a zona da quadra</option>
                    {% for zona in zonas_quadra %}
                    <option value="{{ zona }}">Zona {{ zona }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="tipo_ataque_assistencia" class="form-label">Tipo de Gol (Assistência)</label>
                <select id="tipo_ataque_assistencia" name="tipo_ataque" class="form-select" required>
                    <option value="" disabled selected>Selecione o tipo de gol</option>
                    {% for tipo in tipos_gol %}
                    <option value="{{ tipo }}">{{ tipo|replace("_", " ")|capitalize }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="assistencia_convertida" class="form-label">Assistência Convertida</label>
                <select id="assistencia_convertida" name="assistencia_convertida" class="form-select" required>
                    <option value="" disabled selected>Selecione</option>
                    <option value="true">Sim</option>
                    <option value="false">Não</option>
                </select>
            </div>
            <div class="mb-3">
                <label for="periodo_assistencia" class="form-label">Período</label>
                <select id="periodo_assistencia" name="periodo" class="form-select" required>
                    <option value="" disabled selected>Selecione o período</option>
                    <option value="1">1º Período</option>
                    <option value="2">2º Período</option>
                </select>
            </div>
        </div>

        <!-- Grupo para Ação Defensiva -->
        <div id="grupo_acao_defensiva" style="display:none;">
            <h4>Ação Defensiva</h4>
            <div class="mb-3">
                <label for="jogador_id_defensiva" class="form-label">Número do Jogador</label>
                <select id="jogador_id_defensiva" name="jogador_id" class="form-select" required>
                    <option value="" disabled selected>Selecione o jogador (por número)</option>
                    {% for jogador in jogadores %}
                    <option value="{{ jogador.jogador_id }}">{{ jogador.numero_camisa }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="zona_quadra_defensiva" class="form-label">Zona da Quadra</label>
                <select id="zona_quadra_defensiva" name="zona_quadra" class="form-select" required>
                    <option value="" disabled selected>Selecione a zona da quadra</option>
                    {% for zona in zonas_quadra %}
                    <option value="{{ zona }}">Zona {{ zona }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="tipo_acao" class="form-label">Tipo de Ação</label>
                <select id="tipo_acao" name="tipo_acao" class="form-select" required>
                    <option value="" disabled selected>Selecione a ação defensiva</option>
                    {% for acao in tipos_acao_defensiva %}
                    <option value="{{ acao }}">{{ acao|capitalize }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label for="periodo_defensiva" class="form-label">Período</label>
                <select id="periodo_defensiva" name="periodo" class="form-select" required>
                    <option value="" disabled selected>Selecione o período</option>
                    <option value="1">1º Período</option>
                    <option value="2">2º Período</option>
                </select>
            </div>
        </div>


        <button type="submit" class="btn btn-success w-100">
            <i class="fas fa-check"></i> Registrar Evento
        </button>
    </form>

    <!-- Lista de Eventos Registrados -->
    <h2 class="text-center mt-5">Eventos Registrados</h2>
    <div class="list-group">
        {% for evento in eventos %}
        <div class="list-group-item">
            <strong>{{ evento.tipo_evento|capitalize }}</strong>
            {% if evento.subtipo_evento %} - {{ evento.subtipo_evento|replace("_", " ")|capitalize }}{% endif %}
            {% if evento.parte_corpo %} - {{ evento.parte_corpo|replace("_", " ")|capitalize }}{% endif %}
            {% if evento.zona_quadra_id %} - Zona Quadra: {{ evento.zona_quadra_id }}{% endif %}
            {% if evento.periodo %} - Período: {{ evento.periodo }}{% endif %}
            {% if evento.minuto_evento %} - Minuto: {{ evento.minuto_evento }}{% endif %}
            {% if evento.situacao_jogo %} - Situação: {{ evento.situacao_jogo|capitalize }}{% endif %}
        </div>
        {% else %}
        <div class="list-group-item text-center">

        </div>
        {% endfor %}
    </div>

    <!-- Botão para Encerrar o Jogo Ao Vivo -->
    <form action="/api/jogo_ao_vivo/{{ partida.partida_id }}/encerrar" method="post" class="mt-4">
        <button type="submit" class="btn btn-danger w-100">
            <i class="fas fa-stop"></i> Encerrar Jogo
        </button>
    </form>
</div>

<script>
    // Função para mostrar/ocultar grupos de campos com base na categoria selecionada
    function mostrarGrupo(categoria) {
        document.getElementById("grupo_evento").style.display = "none";
        document.getElementById("grupo_finalizacao").style.display = "none";
        document.getElementById("grupo_assistencia").style.display = "none";
        document.getElementById("grupo_acao_defensiva").style.display = "none";

        if(categoria === "evento") {
            document.getElementById("grupo_evento").style.display = "block";
        } else if(categoria === "finalizacao") {
            document.getElementById("grupo_finalizacao").style.display = "block";
        } else if(categoria === "assistencia") {
            document.getElementById("grupo_assistencia").style.display = "block";
        } else if(categoria === "acao_defensiva") {
            document.getElementById("grupo_acao_defensiva").style.display = "block";
        }
    }
    // Função para exibir o dropdown de jogador conforme o time selecionado
    function mostrarJogador(timeMarcador) {
        if(timeMarcador === "meu") {
            document.getElementById("div_jogador_meu").style.display = "block";
            document.getElementById("div_jogador_adv").style.display = "none";
        } else if(timeMarcador === "adversario") {
            document.getElementById("div_jogador_meu").style.display = "none";
            document.getElementById("div_jogador_adv").style.display = "block";
        }
    }
</script>

<script src="https://kit.fontawesome.com/your-fontawesome-kit.js" crossorigin="anonymous"></script>
{% endblock %}
