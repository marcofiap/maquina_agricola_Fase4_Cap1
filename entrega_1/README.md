# Maquina_Agricola
 Projeto Fase 3 - FIAP
 # FarmTech Solutions - Sistema de Sensores e Controle com ESP32

## Visão Geral do Projeto

## Visão Geral do Projeto

Este projeto simula um sistema de irrigação inteligente para a FarmTech Solutions, utilizando um ESP32 e sensores simulados na plataforma Wokwi. O sistema coleta dados de umidade do solo, simula leituras de pH e níveis de nutrientes (Fósforo e Potássio) e controla automaticamente uma bomba de irrigação com base na umidade do solo. Adicionalmente, o sistema permite o controle manual da irrigação pelo usuário, seguindo as indicações de alerta de chuva fornecidas pelo dashboard com base nas previsões climáticas.

Para facilitar o acompanhamento local, um display OLED conectado ao circuito no Wokwi exibe as grandezas físicas coletadas pelo ESP32. Os dados também são visualizados em tempo real através de um dashboard, apresentado em formato de tabelas, gráficos, condições climáticas e previsões de chuva, auxiliando na análise e tomada de decisão sobre a irrigação.

## Circuito Wokwi

[INSERIR AQUI A IMAGEM DO SEU CIRCUITO WOKWI (.png)]

### Componentes Utilizados:

* **ESP32:** Microcontrolador responsável por ler os sensores e controlar o relé da bomba.
* **DHT22:** Sensor de temperatura e umidade do solo.
* **LDR (Light Dependent Resistor):** Simula o sensor de pH, com valores analógicos variando conforme a luminosidade.
* **Botões (2):** Simulam os sensores de Fósforo (P) e Potássio (K), com leituras binárias (pressionado = presente, solto = ausente).
* **Relé (Simulado por um LED):** Representa a bomba d'água, sendo ligado para irrigar e desligado para interromper.
* **Botão (Pino 15):** Botão manual para desligar a bomba de irrigação.
* **Display OLED:** Exibe localmente as leituras de temperatura, umidade e pH.

### Conexões:

* **DHT22:** Pino de dados conectado ao pino digital 5 do ESP32.
* **LDR:** Conectado a um divisor de tensão e ao pino analógico 34 do ESP32.
* **Botão Fósforo (P):** Conectado ao pino digital 2 do ESP32 (configurado com pull-up interno).
* **Botão Potássio (K):** Conectado ao pino digital 18 do ESP32 (configurado com pull-up interno).
* **Relé (LED):** Conectado ao pino digital 4 do ESP32.
* **Botão Desligar Bomba:** Conectado ao pino digital 15 do ESP32 (configurado com pull-up interno).
* **Display OLED:** Conectado aos pinos I2C do ESP32 (SDA e SCL).

## Lógica de Controle da Bomba de Irrigação

A lógica de controle da bomba de irrigação implementada no ESP32 é a seguinte:

1.  **Irrigação Automática (Baseada na Umidade):**
    * A bomba é ligada (o relé é acionado para HIGH) se a umidade do solo (lida pelo sensor DHT22) for inferior a 40%.
    * A bomba permanece ligada por um período simulado de 5 segundos para simular a irrigação.
    * Após o período de irrigação, a bomba é desligada (o relé é acionado para LOW).
    * A bomba também é desligada automaticamente se a umidade do solo subir acima de 40% enquanto estiver ligada.

2.  **Desligamento Manual (Botão no Pino 15):**
    * Um botão conectado ao pino digital 15 do ESP32 permite o desligamento manual da bomba.
    * Se o botão for pressionado (nível LOW, devido à configuração pull-up) em qualquer momento, a bomba é desligada imediatamente, interrompendo a irrigação automática, caso esteja em andamento.

3.  **Estado da Bomba:**
    * Uma variável booleana (`bombaLigada`) rastreia o estado atual da bomba (ligada ou desligada).
    * O status da bomba (`on` ou `off`) é enviado para o servidor Python via HTTP.

## Código C/C++

O código C/C++ para o ESP32 lê os dados dos sensores, implementa a lógica de controle da bomba e envia os dados para o servidor Python. Os valores dos sensores também são exibidos localmente no display OLED. (O código completo está no arquivo `.ino` do projeto).

## Próximos Passos (Entrega 2)

Na próxima entrega, os dados coletados e exibidos no monitor serial do ESP32 serão utilizados para simular o armazenamento em um banco de dados SQL usando um script Python, juntamente com a implementação das operações CRUD básicas.
