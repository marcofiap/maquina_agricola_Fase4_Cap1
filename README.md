# 🌾 FarmTech Solutions – Sistema de Irrigação Inteligente com ESP32, Python e Clima em Tempo Real

Este repositório apresenta o desenvolvimento completo de um sistema de **agricultura digital inteligente**, com sensores simulados, banco de dados Oracle, API de clima e visualização interativa. O projeto foi desenvolvido como parte da Fase 3 do curso de Inteligência Artificial na FIAP.

---

## 🎯 Objetivo Geral

Criar uma solução completa de **irrigação inteligente**, capaz de:

- Monitorar **umidade, temperatura, pH e nutrientes** do solo em tempo real
- Controlar **automaticamente** (ou manualmente) uma bomba de irrigação via ESP32
- Armazenar os dados em um **banco relacional (Oracle)**
- Visualizar e analisar os dados por meio de um **dashboard interativo**
- Integrar **previsões climáticas reais** para otimizar o uso de água

---

## 🛠️ Tecnologias Utilizadas

- **ESP32** (simulado com Wokwi)
- **C/C++** com PlatformIO (VS Code)
- **Python 3.10+**
  - `oracledb`, `requests`, `dash`, `plotly`, `pandas`, `flask`
- **Banco Oracle XE**
- **API OpenWeatherMap** (dados climáticos em tempo real)
- **Dash + Plotly** (dashboard web interativo)

---

## 📂 Estrutura do Repositório

| Pasta        | Conteúdo                                                  |
|--------------|-----------------------------------------------------------|
| `entrega_1/` | Código C++ do ESP32, lógica de sensores, display, relé    |
| `entrega_2/` | Script Python com operações CRUD em banco Oracle          |
| `entrega_3/` | Dashboard interativo em Python + integração com a API     |

---

## 🔗 Acesse cada parte do projeto:

- 📦 [Entrega 1 – ESP32 e sensores simulados](./entrega_1/)
- 💾 [Entrega 2 – Banco de dados e CRUD Oracle](./entrega_2/)
- 📊 [Entrega 3 – Dashboard com clima em tempo real](./Ir%Alem1_2/)

---

## 🖼️ Visão Geral do Sistema

![Visão completa do dashboard](Ir%20Alem1_2/Dashboard_API_Metereologica/Imagens/DashboardFuncioando.png)

---

## ✅ Status do Projeto

✔️ Circuito funcional com sensores simulados  
✔️ CRUD completo com armazenamento em banco Oracle  
✔️ Integração com API meteorológica  
✔️ Dashboard funcional com gráficos, alertas e automações  
✔️ Documentação completa para cada entrega

---

## 👨‍🏫 Projeto desenvolvido para avaliação na FIAP  
**Curso:** Tecnólogo em Inteligência Artificial  
**Grupo 58** – Professores: Leonardo Ruiz Orabona / André Godoi  
**Integrantes:**
- Felipe Sabino da Silva  
- Juan Felipe Voltolini  
- Luiz Henrique Ribeiro de Oliveira  
- Marco Aurélio Eberhardt Assimpção  
- Paulo Henrique Senise  

---
