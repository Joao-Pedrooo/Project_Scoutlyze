-- ======================================================
-- Script SQL para Inserir Dados Falsos (Dummy Data)
-- para Testar o Sistema de Análise de Futsal.
-- ======================================================

-- 1. Inserção de Times
-- Cria dois times: "Time A" (time pró) e "Time B" (time adv)
INSERT INTO times (time_id, nome, categoria)
VALUES ('TM000001', 'Time A', 'profissional');

INSERT INTO times (time_id, nome, categoria)
VALUES ('TM000002', 'Time B', 'profissional');

-- 2. Inserção de Jogadores para cada time

-- Jogadores do Time A (Time Pró)
INSERT INTO jogadores (jogador_id, time_id, nome, numero_camisa, posicao, pe_dominante, created_at)
VALUES ('JG000001', 'TM000001', 'Jogador A1', '01', 'fixo', 'direito', CURRENT_TIMESTAMP);

INSERT INTO jogadores (jogador_id, time_id, nome, numero_camisa, posicao, pe_dominante, created_at)
VALUES ('JG000002', 'TM000001', 'Jogador A2', '02', 'fixo', 'direito', CURRENT_TIMESTAMP);

INSERT INTO jogadores (jogador_id, time_id, nome, numero_camisa, posicao, pe_dominante, created_at)
VALUES ('JG000003', 'TM000001', 'Jogador A3', '03', 'fixo', 'direito', CURRENT_TIMESTAMP);

INSERT INTO jogadores (jogador_id, time_id, nome, numero_camisa, posicao, pe_dominante, created_at)
VALUES ('JG000004', 'TM000001', 'Jogador A4', '04', 'fixo', 'direito', CURRENT_TIMESTAMP);

INSERT INTO jogadores (jogador_id, time_id, nome, numero_camisa, posicao, pe_dominante, created_at)
VALUES ('JG000005', 'TM000001', 'Jogador A5', '05', 'fixo', 'direito', CURRENT_TIMESTAMP);

-- Jogadores do Time B (Time ADV)
INSERT INTO jogadores (jogador_id, time_id, nome, numero_camisa, posicao, pe_dominante, created_at)
VALUES ('JG000006', 'TM000002', 'Jogador B1', '01', 'fixo', 'esquerdo', CURRENT_TIMESTAMP);

INSERT INTO jogadores (jogador_id, time_id, nome, numero_camisa, posicao, pe_dominante, created_at)
VALUES ('JG000007', 'TM000002', 'Jogador B2', '02', 'fixo', 'esquerdo', CURRENT_TIMESTAMP);

INSERT INTO jogadores (jogador_id, time_id, nome, numero_camisa, posicao, pe_dominante, created_at)
VALUES ('JG000008', 'TM000002', 'Jogador B3', '03', 'fixo', 'esquerdo', CURRENT_TIMESTAMP);

INSERT INTO jogadores (jogador_id, time_id, nome, numero_camisa, posicao, pe_dominante, created_at)
VALUES ('JG000009', 'TM000002', 'Jogador B4', '04', 'fixo', 'esquerdo', CURRENT_TIMESTAMP);

INSERT INTO jogadores (jogador_id, time_id, nome, numero_camisa, posicao, pe_dominante, created_at)
VALUES ('JG000010', 'TM000002', 'Jogador B5', '05', 'fixo', 'esquerdo', CURRENT_TIMESTAMP);

-- 3. Inserção de uma Partida
-- Cria uma partida entre Time A (mandante) e Time B (visitante)
INSERT INTO partidas (
    partida_id, time_casa_id, time_visitante_id, campeonato, fase_competicao,
    rodada, local_partida, data_partida, placar_casa, placar_visitante,
    periodo, minuto_acao, placar_momento, created_at
)
VALUES (
    'PT000001', 'TM000001', 'TM000002', 'Campeonato Teste', 'classificatorio',
    1, NULL, CURRENT_TIMESTAMP, 0, 0, 1, 0, '0x0', CURRENT_TIMESTAMP
);

-- 4. Inserção de Eventos

-- 4.1 Evento de Finalização (Exemplo: Gol)
-- Este evento utiliza a tabela "finalizacoes" e insere um gol do primeiro jogador do Time A.
INSERT INTO finalizacoes (
    finalizacao_id, partida_id, jogador_id, zona_quadra_id, zona_goleira_id,
    tipo_ataque_id, tipo_finalizacao, resultado, periodo
)
VALUES (
    'FN000001', 'PT000001', 'JG000001', 'ZQ0001', 'ZG0001',
    'TA0001', 'chute_rasteiro', 'gol', 1
);

-- 4.2 Evento Simples (Exemplo: Observação ou outro evento não-finalizacao)
-- Insere um evento na tabela "eventos" para o primeiro jogador do Time B.
INSERT INTO eventos (
    evento_id, partida_id, jogador_id, jogador_assistencia_id,
    tipo_evento, subtipo_evento, parte_corpo, zona_quadra_id,
    periodo, minuto_evento, situacao_jogo
)
VALUES (
    'EV000001', 'PT000001', 'JG000006', NULL,
    'evento', 'observacao', 'pe_direito', 'ZQ0001',
    1, 10, 'regular'
);

-- Fim do script de inserção de dados falsos.
