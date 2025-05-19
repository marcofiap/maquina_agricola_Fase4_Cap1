# Sistema de Irrigação Inteligente com ESP32  
### Projeto Fase 3 – FarmTech Solutions | FIAP

Este projeto simula um sistema de irrigação automatizado utilizando o microcontrolador ESP32, sensores físicos (ou simulados) e lógica de controle embarcada. Desenvolvido no simulador Wokwi, o sistema integra leitura de sensores, acionamento de bomba via relé e visualização de dados em um display OLED.

Além disso, os dados dos sensores são enviados via HTTP a um backend Python que registra as informações em um banco SQL e permite visualização futura via dashboard. A lógica permite controle automático da irrigação com base na umidade do solo e também controle **manual** em caso de **previsão de chuva**, com base em dados de uma **API climática**.

---

## 📑 Índice

- [👥 Grupo](#-grupo)
- [📘 Visão Geral](#-visão-geral-do-projeto)
- [🔌 Circuito Wokwi](#-circuito-wokwi)
- [🔧 Componentes](#-componentes-utilizados)
- [⚙️ Conexões](#-conexões)
- [💧 Lógica de Controle](#-lógica-de-controle-da-bomba-de-irrigação)
- [📁 Código](#-código-cc)

---

## 👥 Grupo

**Grupo 58 – FIAP**  
*Integrantes:*
- Felipe Sabino da Silva  
- Juan Felipe Voltolini  
- Luiz Henrique Ribeiro de Oliveira  
- Marco Aurélio Eberhardt Assimpção  
- **Paulo Henrique Senise**  

*Professores:*  
- Tutor: Leonardo Ruiz Orabona  
- Coordenador: André Godoi

---

## 📘 Visão Geral do Projeto

O sistema realiza:
- Leitura da **umidade do solo**, **pH**, **fósforo** e **potássio**.
- Acionamento automático da bomba quando a umidade está abaixo do ideal.
- Controle manual da irrigação por botão físico em caso de previsão de chuva.
- Exibição local dos dados no **display OLED**.
- Envio dos dados via **HTTP GET** para armazenamento em banco SQL.

---

## 🔌 Circuito Wokwi

O projeto foi montado e testado no simulador online [Wokwi](https://wokwi.com). As imagens abaixo mostram os sensores e botões simulados em ação:

> (📷 Substitua os links abaixo por imagens salvas na pasta `/imagens/` no seu repositório)

- Sensor LDR simula o pH
- DHT22 simula temperatura e umidade
- Botões simulam fósforo e potássio
- Relé simulado por LED vermelho
- Display OLED exibe os dados

---

## 🔧 Componentes Utilizados

| Componente        | Função                                  |
|-------------------|------------------------------------------|
| **ESP32**         | Microcontrolador principal                |
| **DHT22**         | Sensor de temperatura e umidade           |
| **LDR**           | Simula leitura de pH                      |
| **Botões (2)**    | Simulam sensores de Fósforo e Potássio    |
| **Botão (15)**    | Desligar manualmente a bomba              |
| **Display OLED**  | Exibe dados locais                        |
| **Relé (LED)**    | Simula bomba de irrigação                 |

---

## ⚙️ Conexões

| Componente            | Pino do ESP32  |
|-----------------------|----------------|
| Sensor DHT22          | Pino 5         |
| Sensor LDR            | Pino 34 (ADC)  |
| Botão Fósforo (P)     | Pino 2         |
| Botão Potássio (K)    | Pino 18        |
| Botão Desligar Bomba  | Pino 15        |
| Relé (LED)            | Pino 4         |
| Display OLED (I2C)    | SDA/SCL        |

---

## 💧 Lógica de Controle da Bomba de Irrigação

### 1. **Automático (baseado na umidade)**
- **Se** umidade < 40% → **Liga** a bomba.
- **Se** umidade >= 40% → **Desliga** a bomba.

### 2. **Manual (previsão de chuva)**
- **Se** o botão do pino 15 for pressionado → **Desliga** a bomba manualmente.
- Esse botão é usado quando o dashboard detecta **chuva futura**.

### 3. **Status**
- A bomba é representada por um **LED vermelho**.
- O estado da bomba é enviado ao servidor Python (`on` ou `off`).

---

## 📁 Código C/C++

O código responsável pela leitura dos sensores, lógica de irrigação e comunicação com o servidor está disponível na pasta:

📂 [`src/programa_esp32`](./src/programa_esp32)

- Os valores dos sensores são exibidos localmente no **display OLED**.
- Dados são enviados via `HTTP GET` para o servidor Flask.
- Todas as leituras são visíveis no **Serial Monitor**.

---

> Caso deseje ver a visualização dos dados e integração com banco/API, acesse as outras entregas na pasta raiz do projeto.
