# FarmTech Solutions – Sistema de Irrigação Inteligente

Este repositório apresenta o desenvolvimento completo de um sistema de **agricultura digital inteligente**.
O projeto foi desenvolvido como parte da Fase 3 do curso de Inteligência Artificial na FIAP.

![Status do Projeto](https://img.shields.io/badge/Entrega%20Concluída-100%25-green)
![ESP32](https://img.shields.io/badge/Hardware-ESP32-lightgrey)
![Banco de Dados](https://img.shields.io/badge/Oracle-CRUD-blue)
![Dashboard](https://img.shields.io/badge/Visualização-Dash%20%2B%20API-orange)
![Análise Preditiva](https://img.shields.io/badge/Análise%20Preditiva-R%20%2B%20Séries%20Temporais-blueviolet)

## Sumário do Projeto

- [Descricao do Projeto](#descricao-do-projeto)
- [Entrega 1 – Controle com ESP32](#entrega-1--controle-com-esp32)
- [Entrega 2 – Banco de Dados e CRUD em Python](#entrega-2--banco-de-dados-e-crud-em-python)
- [Ir Alem – Dashboard Interativo](#ir-alem--dashboard-interativo)
- [Ir Alem – Integracao com API Climatica](#ir-alem--integracao-com-api-climatica)
- [Demonstracao em Video](#demonstracao-em-video)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Como Executar](#como-executar)
- [Autores](#autores)

---

## Objetivo Geral

Criar uma solução completa de **irrigação inteligente**, capaz de:

- Monitorar **umidade, temperatura, pH e nutrientes** do solo em tempo real
- Controlar **automaticamente** (ou manualmente) uma bomba de irrigação via ESP32
- Armazenar os dados em um **banco relacional (Oracle)**
- Visualizar e analisar os dados por meio de um **dashboard interativo**
- Integrar **previsões climáticas reais** para otimizar o uso de água
- Realizar análise estatística preditiva dos dados coletados utilizando R, identificando padrões e antecipando condições ideais de irrigação

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

| Pasta                   | Conteúdo                                                                                        |
|-------------------------|-------------------------------------------------------------------------------------------------|
| `Analise_Estatistica/`  | Códigos em R para análise descritiva (média, desvio padrão) e preditiva (modelos de previsão)   |
| `Ir Alem1_2/`           | Dashboard interativo em Python + integração com a API                                           |
| `Servidor_Local/`       | Código Python, rodar servidor com biblioteca Flask                                              |
| `entrega_1/`            | Código C++ do ESP32, lógica de sensores, display, relé                                          |
| `entrega_2/`            | Script Python com operações CRUD em banco Oracle                                                |


---

## Visão Geral do Sistema Dashboard
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
