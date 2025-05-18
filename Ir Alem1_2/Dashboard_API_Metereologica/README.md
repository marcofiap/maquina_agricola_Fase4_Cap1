# 🌿 FarmTech Solutions - Sistema de Irrigação Inteligente com Dashboard e Clima em Tempo Real

![Sistema de Sensores e Controle com ESP32](https://github.com/user-attachments/assets/467974e1-2cd2-4a9a-a01a-2c7861282489)

## 📌 Descrição do Projeto
Este projeto tem como objetivo simular um sistema de irrigação inteligente que utiliza sensores físicos (simulados) conectados a um ESP32. Os dados dos sensores são enviados para um servidor Flask, armazenados em banco de dados Oracle, e visualizados em tempo real através de um dashboard interativo em Python com a biblioteca Dash.

Além disso, o sistema se integra à API do OpenWeatherMap para prever chuva e exibir dados climáticos da cidade em tempo real.

---

## 👨‍🎓 Grupo 58 - FIAP
### Integrantes:
- Felipe Sabino da Silva
- Juan Felipe Voltolini
- Luiz Henrique Ribeiro de Oliveira
- Marco Aurélio Eberhardt Assimpção
- Paulo Henrique Senise

### Professores:
- **Tutor(a):** Leonardo Ruiz Orabona
- **Coordenador(a):** André Godoi

---

## ⚙️ Tecnologias Utilizadas
- ESP32 (simulado via Wokwi)
- Sensores simulados: DHT22, LDR, botões (fósforo/potássio)
- Python 3.10+
- Flask (servidor HTTP e banco de dados Oracle)
- Oracle Database XE
- Dash (visualização interativa)
- OpenWeatherMap API (clima atual)

---

## 🧪 Funcionalidades do Dashboard
- Leitura de sensores: umidade, temperatura, pH (via LDR), fósforo e potássio
- Acionamento de bomba via relé (simulado)
- Envio dos dados via HTTP para servidor Flask
- Armazenamento em banco Oracle
- Dashboard com:
  - Gráficos de umidade e temperatura
  - Estado da bomba (ligada/desligada)
  - Indicadores de fósforo e potássio
  - Tabela de dados em tempo real
  - Painel de clima atual (temperatura, vento, céu, etc.)
  - Alerta de chuva (visual)

---

## 🚀 Como Executar o Projeto

### 1. ESP32 (via Wokwi)
- Monte o circuito no [https://wokwi.com/](https://wokwi.com/)
- Use o código em C/C++ para ler sensores e enviar via Wi-Fi

### 2. Servidor Flask
```bash
python flask_server.py
```
- Certifique-se de que o Oracle DB esteja ativo
- O servidor roda em `http://localhost:8000`

### 3. Dashboard em Dash
```bash
python dashboard.py
```
- Acesse via navegador: `http://127.0.0.1:8050`

### 4. API de Clima
- Crie conta no [OpenWeatherMap](https://openweathermap.org/api)
- Substitua a chave no código:
```python
API_KEY = "SUA_CHAVE_AQUI"
```

---

## 🌦️ Ir Além 2: Integração com API de Previsão do Tempo
O sistema se conecta à **API OpenWeatherMap** para buscar dados climáticos atuais e previsão para as próximas 12 horas. Baseado nisso:

### Lógica Condicional para Irrigação:
- Se houver previsão de chuva, **bomba é desligada**
- Se a umidade do solo for > 40%, **bomba é desligada**
- Se a temperatura for < 18°C, **bomba é desligada**

Isso evita desperdício de água e melhora a eficiência do sistema.

---

## 📸 Capturas de Tela do Dashboard
![DashBoardCompletoeFuncionando](https://github.com/user-attachments/assets/a50a58ca-055b-48bd-b303-c76cdc0c4fba)

---

## 🧠 Código Python - Exemplo de Integração com a API
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

## 👩‍🏫 Considerações Finais
O dashboard em Python oferece uma interface visual e informativa para monitorar sensores agrícolas, com auxílio de dados meteorológicos reais, simulando um sistema de irrigação inteligente completo.

---



