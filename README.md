## Sistema de Irrigacao Inteligente – Fase 3 | FarmTech Solutions

![Status](https://img.shields.io/badge/status-concluído-brightgreen)
![CRUD Oracle](https://img.shields.io/badge/CRUD-implementado-blue)
![Dashboard](https://img.shields.io/badge/dashboard-ativo-orange)
![API Climática](https://img.shields.io/badge/API%20Climática-integrada-lightgrey)

---

## Sumario do Projeto

- [Descricao do Projeto](#descricao-do-projeto)
- [Entrega 1 – Controle com ESP32](#entrega-1--controle-com-esp32)
- [Entrega 2 – Banco de Dados e CRUD em Python](#entrega-2--banco-de-dados-e-crud-em-python)
- [Ir Alem – Dashboard Interativo](#ir-alem--dashboard-interativo)
- [Ir Alem – Integracao com API Climatica](#ir-alem--integracao-com-api-climatica)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Como Executar](#como-executar)
- [Autores](#autores)

---

## Descricao do Projeto

Este projeto simula um sistema de **irrigacao agricola inteligente**, utilizando sensores fisicos (ou simulados) conectados a um ESP32. O sistema monitora parametros como **umidade, pH e presenca de nutrientes (Fosforo e Potassio)**. A bomba de irrigacao é acionada automaticamente de acordo com a logica implementada.

Alem disso, os dados sao armazenados em um **banco de dados relacional Oracle**, visualizados por meio de uma **dashboard Python**, e o sistema se conecta a uma **API meteorologica** para tomada de decisoes mais inteligentes.

---

## Entrega 1 – Controle com ESP32

- Simulacao feita na plataforma Wokwi
- Sensores utilizados:
  - DHT22 → Umidade
  - LDR → pH (simulado)
  - Botoes → Fosforo e Potassio (presente/ausente)
- Bomba controlada por rele
- LED indica status da irrigacao
- Logica em C++ com comentarios explicativos

---

## Entrega 2 – Banco de Dados e CRUD em Python

- Script em Python com interface ao banco Oracle
- Operacoes:
  - Insercao de dados simulados
  - Consulta de registros
  - Atualizacao de valores
  - Remocao de registros
- Estrutura baseada no MER da Fase 2

📂 [Ver pasta `entrega_2/`](./entrega_2/)

---

## Ir Alem – Dashboard Interativo

Dashboard desenvolvida em Python utilizando Dash ou Streamlit:

- Graficos de:
  - Umidade
  - Status da irrigacao (bomba)
  - Variacoes de pH
  - Nutrientes no solo
- Atualizacao com dados simulados

📂 [Ver pasta `Ir Alem1_2/`](./Ir%20Alem1_2/)

---

## Ir Alem – Integracao com API Climatica

Integracao com a **API OpenWeather**:

- Consulta a previsao do tempo em tempo real
- Decisao de irrigacao influenciada pela chuva prevista
- Mensagem de alerta exibida no sistema se houver chuva

**Logica:**
```python
if previsao_chuva > 0:
    status_irrigacao = "Desligada (chuva prevista)"
```

## Tecnologias Utilizadas

- ESP32 (simulado no Wokwi)
- C/C++ (PlatformIO)
- Python 3
- SQLite / Oracle DB
- Dash / Streamlit
- API OpenWeather

---

## Como Executar

1. Clone o repositorio:
   ```bash
   git clone https://github.com/PauloSenise/maquina_agricola.git
   ```

2. Navegue ate as pastas `entrega_1`, `entrega_2`, `Ir Alem1_2`

3. Siga as instrucoes nos respectivos `README.md` locais

---

## Autores
**Grupo 58 – FIAP**  
*Integrantes:*
- Felipe Sabino da Silva  
- Juan Felipe Voltolini  
- Luiz Henrique Ribeiro de Oliveira  
- Marco Aurélio Eberhardt Assimpção  
- Paulo Henrique Senise 

**Professores:**  
- Tutor: Leonardo Ruiz Orabona  
- Coordenador: André Godoi

