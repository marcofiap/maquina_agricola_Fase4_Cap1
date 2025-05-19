# FarmTech Solutions – Sistema de Irrigação Inteligente com ESP32, Python e Clima em Tempo Real

Este repositório apresenta o desenvolvimento completo de um sistema de **agricultura digital inteligente**, com sensores simulados, banco de dados Oracle, API de clima e visualização interativa. O projeto foi desenvolvido como parte da Fase 3 do curso de Inteligência Artificial na FIAP.

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

## Acesse cada parte do projeto:

-  [Análise Estatística – Dados Oracle](./Analise_Estatistica/)
-  [Entrega 1 – ESP32 e Sensores Simulados](./entrega_1/)
-  [Entrega 2 – Banco de Dados e CRUD Oracle](./entrega_2/)
-  [Ir Além 1 e 2 – Dashboard com Clima em Tempo Real](./Ir%20Alem1_2/Dashboard_API_Metereologica/)

---

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

# Análise Estatística e Preditiva – FarmTech Solutions

[Análise Estatística e Previsão (R)](./Analise_Estatistica/)

## Melhoria Futura Implementável – Irrigação Preditiva

O sistema pode evoluir para incorporar uma lógica **inteligente de desligamento automático da bomba**, com base na **quantidade de chuva prevista** (em milímetros) nas próximas horas.

### Exemplo de lógica:
- Se a previsão for ≥ 3.0 mm de chuva nas próximas 3h → alerta visual para não irrigar

Essa abordagem torna o sistema **ainda mais eficiente**, evitando irrigação desnecessária e otimizando o uso da água com base em dados climáticos reais.

---

## Projeto desenvolvido para avaliação na FIAP  
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
