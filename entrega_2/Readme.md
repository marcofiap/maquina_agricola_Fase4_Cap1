# FarmTech Solutions - Sistema de Irrigação Inteligente com Dashboard e Clima em Tempo Real

![Sistema de Sensores e Controle com ESP32](https://github.com/user-attachments/assets/467974e1-2cd2-4a9a-a01a-2c7861282489)

## Descrição do Projeto

Este projeto tem como objetivo simular um sistema de irrigação inteligente que utiliza sensores físicos (simulados) conectados a um ESP32. Os dados dos sensores são enviados para um servidor Flask, armazenados em banco de dados Oracle, e visualizados em tempo real através de um dashboard interativo em Python com a biblioteca Dash.

Além disso, o sistema se integra à API do OpenWeatherMap para prever chuva e exibir dados climáticos da cidade em tempo real.

---

## Grupo 58 - FIAP

### Integrantes:

* Felipe Sabino da Silva
* Juan Felipe Voltolini
* Luiz Henrique Ribeiro de Oliveira
* Marco Aurélio Eberhardt Assimpção
* Paulo Henrique Senise

### Professores:

* **Tutor(a):** Leonardo Ruiz Orabona
* **Coordenador(a):** André Godoi

---

## Tecnologias Utilizadas

* ESP32 (simulado via Wokwi)
* Sensores simulados: DHT22, LDR, botões simulando nutrientes (fósforo/potássio)
* Python 3.10+
* Flask (servidor HTTP e banco de dados Oracle)
* Oracle Database XE
* Dash (visualização interativa)
* OpenWeatherMap API (clima atual)

---

## Entrega 2: Armazenamento de Dados em Banco SQL com Python

### Objetivo

Armazenar os dados de sensores enviados via ESP32 em um banco Oracle local, utilizando Python e operações CRUD completa.

### Estrutura da Tabela

A tabela `leituras_sensores` representa o modelo lógico criado na fase anterior (MER), e possui os seguintes campos:

| Campo        | Tipo        | Descrição                                     |
| ------------ | ----------- | --------------------------------------------- |
| timestamp    | VARCHAR2    | Identificador único com data/hora             |
| umidade      | NUMBER(5,2) | Umidade do solo em porcentagem (%)            |
| temperatura  | NUMBER(5,2) | Temperatura do solo (°C)                      |
| ph           | NUMBER(4,2) | Nível de pH do solo                           |
| fosforo      | VARCHAR2    | Presença de fósforo ("presente" ou "ausente") |
| potassio     | VARCHAR2    | Presença de potássio                          |
| bomba_dagua  | VARCHAR2    | Status da bomba ("on" ou "off")               |

### Justificativa da Estrutura

A escolha dos campos representa diretamente os sensores conectados ao ESP32:

* Umidade e temperatura via DHT22
* pH via sensor LDR (simulação)
* Fósforo e potássio via botões (booleanos simulados)
* Estado do relé representando a bomba de irrigação

A chave primária `timestamp` garante que cada leitura seja única e rastreável no tempo.

### Operações CRUD Implementadas

As seguintes operações estão disponíveis via Python:

| Operação   | Função/Descrição                                          |
| ---------- | --------------------------------------------------------- |
| **Create** | Inserção de uma nova leitura no banco com dados simulados |
| **Read**   | Listagem completa das leituras                            |
| **Read**   | Consulta de leituras por umidade acima de um limite       |
| **Update** | Atualização de dados com base no `timestamp`              |
| **Delete** | Remoção de uma leitura específica                         |

### Exemplo de Criação da Tabela em Oracle (via Python)

```python
import oracledb

conn = oracledb.connect(user="system", password="sua_senha", dsn="localhost:1521/xe")
cursor = conn.cursor()

cursor.execute("""
    BEGIN
        EXECUTE IMMEDIATE '
        CREATE TABLE leituras_sensores (
            timestamp VARCHAR2(50) PRIMARY KEY,
            umidade NUMBER(5,2),
            temperatura NUMBER(5,2),
            ph NUMBER(4,2),
            fosforo VARCHAR2(10),
            potassio VARCHAR2(10),
            bomba_dagua VARCHAR2(10)
        )';
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLCODE != -955 THEN RAISE;
            END IF;
    END;
""")
conn.commit()
cursor.close()
conn.close()
```

---

## Funcionalidades do Dashboard

* Leitura de sensores: umidade, temperatura, pH (via LDR), fósforo e potássio
* Acionamento de bomba via relé (simulado)
* Envio dos dados via HTTP para servidor Flask
* Armazenamento em banco Oracle
* Dashboard com:

  * Gráficos de umidade e temperatura
  * Estado da bomba (ligada/desligada)
  * Indicadores de fósforo e potássio
  * Tabela de dados em tempo real
  * Painel de clima atual (temperatura, vento, céu, etc.)
  * Alerta de chuva (visual) para desligamento manual da bomba via botão, em caso da bomba estiver ligada

---

## Como Executar o Projeto

### 1. ESP32 (via Wokwi)

* Monte o circuito no [https://wokwi.com/](https://wokwi.com/)
* Use o código em C/C++ para ler sensores e enviar via Wi-Fi

### 2. Servidor Flask

```bash
python flask_server.py
```

* Certifique-se de que o Oracle DB esteja ativo
* O servidor roda em `http://localhost:8000`

### 3. Dashboard em Dash

```bash
python dashboard.py
```

* Acesse via navegador: `http://127.0.0.1:8050`

### 4. API de Clima

* Crie conta no [OpenWeatherMap](https://openweathermap.org/api)
* Substitua a chave no código:

```python
API_KEY = "SUA_CHAVE_AQUI"
```

---

## Ir Além 2: Integração com API de Previsão do Tempo

O sistema se conecta à **API OpenWeatherMap** para buscar dados climáticos atuais e previsão para as próximas 12 horas. Baseado nisso:

### Lógica Condicional para Irrigação:

* Se houver previsão de chuva, **bomba deve ser desligada manualmente, via botão no esp32**
* Se a umidade do solo for > 40%, **bomba é desligada**
* Se a temperatura for < 18°C, **bomba é desligada**

**Isso evita desperdício de água e melhora a eficiência do sistema.**

---

## Capturas de Tela do Dashboard

![DashBoardCompletoeFuncionando](https://github.com/user-attachments/assets/a50a58ca-055b-48bd-b303-c76cdc0c4fba)

---

## Código Python - Exemplo de Integração com a API

```python
import requests

API_KEY = "CHAVE_DA_API"
cidade = "Porto Alegre"

url_previsao = f"https://api.openweathermap.org/data/2.5/forecast?q={cidade},BR&appid={API_KEY}&units=metric&lang=pt_br&cnt=4"
response = requests.get(url_previsao)
data = response.json()

aviso = ""
for item in data['list']:
    if 'rain' in item and item['rain'].get('3h', 0) > 0:
        aviso = "⚠️ Previsão de chuva! Desligar bomba."
        break
```

---

## Uso do Script Simulador CRUD Oracle

Para facilitar os testes manuais sem depender do ESP32 ou do servidor Flask, foi criado o script `crud_simulador_oracle.py`, que permite executar operações diretamente no banco Oracle local.

### Como executar:

```bash
python crud_simulador_oracle.py
```

### Menu interativo:

```
========= MENU CRUD =========
1 - Inserir nova leitura
2 - Listar todas as leituras
3 - Atualizar uma leitura
4 - Remover uma leitura
0 - Sair
============================
```

### Funcionalidades:

* **Inserção manual** de dados de sensores
* **Listagem** das leituras ordenadas por timestamp
* **Atualização** com base em um timestamp existente
* **Remoção** de uma leitura específica

> ⚠️ Atenção: Altere a variável `DB_PASSWORD` no script com sua senha real do Oracle antes de rodar.

---

## Considerações Finais

O dashboard em Python oferece uma interface visual e informativa para monitorar sensores agrícolas, com auxílio de dados meteorológicos reais, simulando um sistema de irrigação inteligente completo.

---


