-- Script de inicialização do banco de dados para FarmTech Solutions
-- Este script insere os dados básicos necessários para o funcionamento do sistema CRUD

-- Limpar dados existentes (caso necessário reiniciar)
-- Importante: execute na ordem correta para respeitar as restrições de chaves estrangeiras

DELETE FROM monitoramento;
DELETE FROM agua_aplicada;
DELETE FROM vitaminas_aplicadas;
DELETE FROM sensor_tipo_sensor;
DELETE FROM calibracao_sensor;
DELETE FROM sensor;
DELETE FROM cultura;
DELETE FROM tipo_sensor;
DELETE FROM vitaminas;
DELETE FROM unidade_medida;

-- Inserir unidades de medida básicas
INSERT INTO unidade_medida (id_unidade_medida, descricao, abreviacao) VALUES (1, 'Temperatura', '°C');
INSERT INTO unidade_medida (id_unidade_medida, descricao, abreviacao) VALUES (2, 'Umidade', '%');
INSERT INTO unidade_medida (id_unidade_medida, descricao, abreviacao) VALUES (3, 'pH', 'pH');
INSERT INTO unidade_medida (id_unidade_medida, descricao, abreviacao) VALUES (4, 'Presença', 'b');
INSERT INTO unidade_medida (id_unidade_medida, descricao, abreviacao) VALUES (5, 'Estado do Relé', 'b');
INSERT INTO unidade_medida (id_unidade_medida, descricao, abreviacao) VALUES (6, 'Volume', 'L');
INSERT INTO unidade_medida (id_unidade_medida, descricao, abreviacao) VALUES (7, 'Peso', 'kg');


-- Inserir tipos de sensores
INSERT INTO tipo_sensor (id_tipo_sensor, id_unidade_medida, descricao) VALUES (1, 1, 'Temperatura');
INSERT INTO tipo_sensor (id_tipo_sensor, id_unidade_medida, descricao) VALUES (2, 2, 'Umidade');
INSERT INTO tipo_sensor (id_tipo_sensor, id_unidade_medida, descricao) VALUES (3, 3, 'pH');
INSERT INTO tipo_sensor (id_tipo_sensor, id_unidade_medida, descricao) VALUES (4, 4, 'Fósforo');
INSERT INTO tipo_sensor (id_tipo_sensor, id_unidade_medida, descricao) VALUES (5, 4, 'Potássio');
INSERT INTO tipo_sensor (id_tipo_sensor, id_unidade_medida, descricao) VALUES (6, 5, 'Bomba de Água');


-- Inserir culturas de exemplo
INSERT INTO cultura (id_cultura, descricao_cultura, ativo, area_plantada) VALUES (1, 'Milho', 'S', 1000);
INSERT INTO cultura (id_cultura, descricao_cultura, ativo, area_plantada) VALUES (2, 'Soja', 'S', 2000);
INSERT INTO cultura (id_cultura, descricao_cultura, ativo, area_plantada) VALUES (3, 'Tomate', 'S', 500);
INSERT INTO cultura (id_cultura, descricao_cultura, ativo, area_plantada) VALUES (4, 'Alface', 'S', 300);
INSERT INTO cultura (id_cultura, descricao_cultura, ativo, area_plantada) VALUES (5, 'Café', 'S', 5000);

-- Inserir sensores para receber dados do ESP32
-- Os sensores são criados para a cultura de Milho (id_cultura=1)
INSERT INTO sensor (id_sensor, id_cultura, numero_serie, ativo) VALUES (1, 1, 'TEMP-001', 'S');
INSERT INTO sensor (id_sensor, id_cultura, numero_serie, ativo) VALUES (2, 1, 'UMID-001', 'S');
INSERT INTO sensor (id_sensor, id_cultura, numero_serie, ativo) VALUES (3, 1, 'PH-001', 'S');
INSERT INTO sensor (id_sensor, id_cultura, numero_serie, ativo) VALUES (4, 1, 'FOSFORO-001', 'S');
INSERT INTO sensor (id_sensor, id_cultura, numero_serie, ativo) VALUES (5, 1, 'POTASSIO-001', 'S');
INSERT INTO sensor (id_sensor, id_cultura, numero_serie, ativo) VALUES (6, 1, 'RELE-001', 'S');

-- Associar sensores aos tipos de sensores
INSERT INTO sensor_tipo_sensor (id_sensor, id_tipo_sensor) VALUES (1, 1); -- Sensor 1 é do tipo Temperatura
INSERT INTO sensor_tipo_sensor (id_sensor, id_tipo_sensor) VALUES (2, 2); -- Sensor 2 é do tipo Umidade
INSERT INTO sensor_tipo_sensor (id_sensor, id_tipo_sensor) VALUES (3, 3); -- Sensor 3 é do tipo pH
INSERT INTO sensor_tipo_sensor (id_sensor, id_tipo_sensor) VALUES (4, 4); -- Sensor 4 é do tipo Fósforo
INSERT INTO sensor_tipo_sensor (id_sensor, id_tipo_sensor) VALUES (5, 5); -- Sensor 5 é do tipo Potássio
INSERT INTO sensor_tipo_sensor (id_sensor, id_tipo_sensor) VALUES (6, 6); -- Sensor 6 é do tipo Bomba de Água

-- Inserir dados de exemplo para vitaminas (nutrientes para plantas)
INSERT INTO vitaminas (id_vitamina, id_unidade_medida, nome, ativo, descricao) 
VALUES (1, 7, 'Nitrogênio', 'S', 'Essencial para o crescimento vegetativo e desenvolvimento de folhas');

INSERT INTO vitaminas (id_vitamina, id_unidade_medida, nome, ativo, descricao) 
VALUES (2, 7, 'Fósforo', 'S', 'Importante para o desenvolvimento de raízes e flores');

INSERT INTO vitaminas (id_vitamina, id_unidade_medida, nome, ativo, descricao) 
VALUES (3, 7, 'Potássio', 'S', 'Auxilia na resistência a doenças e qualidade dos frutos');

-- Inserir calibração inicial para os sensores
INSERT INTO calibracao_sensor (id_sensor, data_calibracao, fator_calibracao, responsavel)
VALUES (1, TIMESTAMP '2025-05-01 09:00:00', 1.0, 'Técnico Sistema');

INSERT INTO calibracao_sensor (id_sensor, data_calibracao, fator_calibracao, responsavel)
VALUES (2, TIMESTAMP '2025-05-01 09:15:00', 1.0, 'Técnico Sistema');

INSERT INTO calibracao_sensor (id_sensor, data_calibracao, fator_calibracao, responsavel)
VALUES (3, TIMESTAMP '2025-05-01 09:30:00', 1.0, 'Técnico Sistema');

-- Verificar se os dados foram inseridos corretamente
COMMIT;

-- Mensagem de confirmação
SELECT 'Dados iniciais inseridos com sucesso!' AS mensagem FROM dual;