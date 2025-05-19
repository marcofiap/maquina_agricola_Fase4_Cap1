# Entrega 3 – Dashboard Interativo com Clima em Tempo Real  
### Projeto Fase 3 – FarmTech Solutions | FIAP

Nesta entrega, foi desenvolvido um sistema de visualização e análise de dados agrícolas com foco em irrigação inteligente. O dashboard foi implementado com a biblioteca Dash (Python) e se conecta a um banco Oracle contendo os dados enviados pelo ESP32. Além disso, o sistema integra a API OpenWeatherMap para exibir condições climáticas em tempo real e prever chuva, auxiliando o operador na tomada de decisão.

---

## Grupo 58 - FIAP

**Integrantes:**
- Felipe Sabino da Silva  
- Juan Felipe Voltolini  
- Luiz Henrique Ribeiro de Oliveira  
- Marco Aurélio Eberhardt Assimpção  
- Paulo Henrique Senise  

**Professores:**  
- Tutor: Leonardo Ruiz Orabona  
- Coordenador: André Godoi

---

## Objetivos da Entrega

- Apresentar os dados de sensores simulados em gráficos interativos
- Exibir o status da bomba de irrigação
- Mostrar presença ou ausência dos nutrientes fósforo e potássio
- Integrar dados meteorológicos com a API OpenWeatherMap
- Emitir alertas visuais em caso de previsão de chuva

---

## Tecnologias Utilizadas

- Python 3.10+
- Dash (plotly, dcc, html, callbacks)
- Banco Oracle (via script da Entrega 2)
- API OpenWeatherMap
- ESP32 (simulado via Wokwi)
- Flask (servidor para comunicação entre ESP32 e banco)

---

## Como Executar

1. **Servidor Flask**
```bash
python flask_server.py
```

2. **Dashboard**
```bash
python dashboard.py
```

3. **Acesso**
- Navegue até `http://127.0.0.1:8050` para visualizar o dashboard.

4. **API de Clima**
- Crie uma conta em [OpenWeatherMap](https://openweathermap.org/api)
- Substitua a chave no código:
```python
API_KEY = "SUA_CHAVE_AQUI"
```

---

## Dashboard com Dados em Tempo Real

O dashboard desenvolvido em Dash apresenta dados atualizados dos sensores e estado da bomba:

![MensagemAlertaChuvaDashboard](https://github.com/user-attachments/assets/c8139400-eb5f-4c6e-b601-fdb806f940aa)

---

## Resposta Manual com Base na Previsão de Chuva

Ao detectar previsão de chuva, o operador pode desligar a bomba manualmente por meio do botão físico no ESP32:

![AposMSGdeAlertaDashbBotaoESP32PressionadoDesligBombaMSGMonitorSerial](https://github.com/user-attachments/assets/6c9088ca-e051-44cd-a1bb-7ca3ce09d540)

---

## Visão Completa do Dashboard

Abaixo, a visão geral do dashboard, exibindo todos os recursos implementados:

![DashboardFuncioando](https://github.com/user-attachments/assets/cc48b61f-b78b-4f4d-9f4f-57e0580d2e50)

---

## Lógica de Integração com a API de Clima

Trecho de código usado para prever chuva nas próximas horas:

```python
import requests

API_KEY = "SUA_CHAVE"
cidade = "Porto Alegre"
url_previsao = f"https://api.openweathermap.org/data/2.5/forecast?q={cidade},BR&appid={API_KEY}&units=metric&lang=pt_br&cnt=4"

response = requests.get(url_previsao)
data = response.json()

alerta = ""
for item in data['list']:
    if 'rain' in item and item['rain'].get('3h', 0) > 0:
        alerta = "⚠️ Previsão de chuva! Desligar bomba."
        break
```

---

## Tomada de Decisão Inteligente

O sistema segue a seguinte lógica:
- Se **umidade > 40%** → bomba é desligada
- Se **temperatura < 18°C** → bomba é desligada
- Se **previsão de chuva** → alerta visual no dashboard para desligamento manual

---

## Status da Entrega

- Dashboard interativo funcional  
- Gráficos e indicadores visuais de sensores  
- Consulta ao banco Oracle com atualização automática  
- Integração com API OpenWeatherMap  
- Lógica condicional para evitar irrigação em caso de chuva  
- Ação manual sincronizada com eventos externos  

---
