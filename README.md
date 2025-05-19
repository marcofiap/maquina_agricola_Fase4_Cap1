# FarmTech Solutions – Sistema de Irrigação Inteligente

Este repositório apresenta o desenvolvimento completo de um sistema de **agricultura digital inteligente**.
O projeto foi desenvolvido como parte da Fase 3 do curso de Inteligência Artificial na FIAP.

![Status do Projeto](https://img.shields.io/badge/Entrega%20Concluída-100%25-green)
![ESP32](https://img.shields.io/badge/Hardware-ESP32-lightgrey)
![Banco de Dados](https://img.shields.io/badge/Oracle-CRUD-blue)
![Dashboard](https://img.shields.io/badge/Visualização-Dash%20%2B%20API-orange)
![Análise Preditiva](https://img.shields.io/badge/Análise%20Preditiva-R%20%2B%20Séries%20Temporais-blueviolet)

## Sumário do Projeto

-  [Entrega 1 – Sensores e Controle com ESP32](./entrega_1/)
  - [`programa_esp32.ino`](./entrega_1/src/programa_esp32.ino) – Código principal
  - Lógica de irrigação automática com sensores simulados (umidade, pH, P, K)
  - Controle do relé e display OLED com alertas

-  [Entrega 2 – Banco de Dados Oracle com CRUD em Python](./entrega_2/)
  - [`crud_simulador_oracle.py`](./entrega_2/crud_simulador_oracle.py)
  - Operações de inserção, consulta, atualização e remoção
  - Estrutura da tabela relacionada ao MER da Fase 2

-  [Ir Além 1 e 2 – Dashboard com API de Clima em Tempo Real](./Ir%20Alem1_2/Dashboard_API_Metereologica/)
  - [`dashboard.py`](./Ir%20Alem1_2/Dashboard_API_Metereologica/dashboard.py)
  - Gráficos de sensores, status da bomba, clima em tempo real (OpenWeatherMap)
  - Alerta visual de chuva com suporte a decisão manual

-  [Análise Estatística e Preditiva (R)](./Analise_Estatistica/)
  - Estatísticas descritivas, boxplots, séries temporais com ARIMA
  - Previsão de umidade futura baseada em dados do banco

---

## Objetivo Geral

Criar uma solução completa de **irrigação inteligente**, capaz de:

- Monitorar **umidade, temperatura, pH e nutrientes** do solo em tempo real
- Controlar **automaticamente** (ou manualmente) uma bomba de irrigação via ESP32
- Armazenar os dados em um **banco relacional (Oracle)**
- Visualizar e analisar os dados por meio de um **dashboard interativo**
- Integrar **previsões climáticas reais** para otimizar o uso de água

---

## Tecnologias Utilizadas

- **ESP32** (simulado com Wokwi)
- **C/C++** com PlatformIO (VS Code)
- **Python 3.10+**
  - `oracledb`, `requests`, `dash`, `plotly`, `pandas`, `flask`
- **Banco Oracle XE**
- **API OpenWeatherMap** (dados climáticos em tempo real)
- **Dash + Plotly** (dashboard web interativo)

---

## Estrutura do Repositório

| Pasta                   | Conteúdo                                                  |
|-------------------------|-----------------------------------------------------------|
| `Analise_Estatistica/`  | Código R, Análise média, media, desvio padrão, previsão   |
| `Ir Alem1_2/`           | Dashboard interativo em Python + integração com a API     |
| `Servidor_Local/`       | Código Python, rodar servidor com biblioteca Flask        |
| `entrega_1/`            | Código C++ do ESP32, lógica de sensores, display, relé    |
| `entrega_2/`            | Script Python com operações CRUD em banco Oracle          |


---

## Imagens do Projeto Eletrônico

- Detalhes individuais dos componentes utilizados no circuito simulador eletrônico
![ComponentesEletronicos](https://github.com/user-attachments/assets/d4cb7f36-a7ce-4803-af37-cd8949f2ffbd)

- Visão geral do projeto montado
![CircuitoMontadoSimulador](https://github.com/user-attachments/assets/7d1bc44a-0881-43e7-bbf6-208411a68dbc)

## Visão Geral do Sistema

![Visão completa do dashboard](Ir%20Alem1_2/Dashboard_API_Metereologica/Imagens/DashboardFuncioando.png)

---

## Status do Projeto

- Circuito funcional com sensores simulados  
- CRUD completo com armazenamento em banco Oracle  
- Integração com API meteorológica  
- Dashboard funcional com gráficos, alertas e automações  
- Documentação completa para cada entrega
- Análise estatística em R

---

## Previsões Climáticas - Lógica Atual e Possível Evolução – Irrigação Preditiva
Atualmente, o sistema já possui uma lógica inteligente de desligamento da bomba em caso de previsão de chuva, com base em dados climáticos consultados via API.
Se a bomba estiver ligada e houver previsão de chuva, um alerta visual é acionado.
Para maior controle, o sistema permite o desligamento manual da bomba pelo botão no ESP32, somente quando ela estiver ligada automaticamente devido à umidade inferior a 40%.

## Possível Melhoria Futura:
A lógica pode ser aprimorada para considerar a quantidade de chuva prevista (em mm) e o intervalo de tempo.
Por exemplo:

Se a previsão for ≥ 3.0 mm de chuva nas próximas 3h → alerta visual e suspensão da irrigação

Essa evolução tornaria o sistema ainda mais eficiente, evitando irrigação desnecessária e otimizando o uso de água com base em dados mais precisos.

---

## Projeto Desenvolvido para Avaliação na FIAP  
**Curso:** Tecnólogo em Inteligência Artificial  
**Grupo 58**  
- Professores: André Godoi
- Tutor: Leonardo Ruiz Orabona
  
**Integrantes:**
- Felipe Sabino da Silva  
- Juan Felipe Voltolini  
- Luiz Henrique Ribeiro de Oliveira  
- Marco Aurélio Eberhardt Assimpção  
- Paulo Henrique Senise  

---
