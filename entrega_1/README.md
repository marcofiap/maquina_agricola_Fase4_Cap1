# Maquina_Agricola
 Projeto Fase 3 - FIAP
 # FarmTech Solutions - Sistema de Sensores e Controle com ESP32

## Visão Geral do Projeto

Este projeto simula um sistema de irrigação inteligente para a FarmTech Solutions, utilizando um ESP32 e sensores simulados na plataforma Wokwi. O sistema coleta dados de umidade do solo, simula leituras de pH e níveis de nutrientes (Fósforo e Potássio) e controla automaticamente uma bomba de irrigação com base na umidade do solo. Adicionalmente, o sistema permite o controle manual da irrigação pelo usuário, seguindo as indicações de alerta de chuva fornecidas pelo dashboard com base nas previsões climáticas.

Para facilitar o acompanhamento local, um display OLED conectado ao circuito no Wokwi exibe as grandezas físicas coletadas pelo ESP32. Os dados também são visualizados em tempo real através de um dashboard, apresentado em formato de tabelas, gráficos, condições climáticas e previsões de chuva, auxiliando na análise e tomada de decisão sobre a irrigação.

## Circuito Wokwi
* Circuito montado no simulador wokwi e funcionando.
![{4217235E-FFF3-487A-9F3B-5A85030145D6}](https://github.com/user-attachments/assets/0997e5f3-63be-4ba2-af87-7304838a6367)
* O sensor LDR sendo variado para simular a lógica do pH (ver display Oled).
![{11348D9C-31EB-4D85-A726-8CF698791E9B}](https://github.com/user-attachments/assets/c918b9b5-cff2-4a4b-98a4-f91859953572)
* O sensor DHT22 sendo variado para simular a lógica de temperatura e umidade (ver display Oled).
![{3C9E2132-2E48-4ED4-B1AD-1586886FEC2A}](https://github.com/user-attachments/assets/73d38647-ca94-4695-a5a5-ecff9594e71f)
* O botão azul apertado simulando o sensor de Potássio (k) = true (ver display Oled).
![{EE6152C4-0433-4732-9D7F-F61FCD4C71C7}](https://github.com/user-attachments/assets/f2897d8a-19a8-4ecf-a9e3-49c5c1c81269)
* O botão amarelo apertado simulando o sensor de Fósforo (P) = true (ver display Oled).
![{087AB5C3-B1CC-4D57-AD6C-0937B0CE704E}](https://github.com/user-attachments/assets/ce4708d8-ca46-44ff-8daf-0b808e03fd51)
* Umidade abaixo de 40% e a bomba estava ligada (led simulando a bomba) ao pressionar o botão a bomba (led) desligou (ver display Oled).
![{EACDDBA9-F1CD-4CC6-8ED0-3A8B912DABF7}](https://github.com/user-attachments/assets/d0341cae-5fb9-4de8-9547-e2fb6e5e3c51)

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
    * O deligamento ocorre somente quando o dashboard emitir um alerta de previsão de chuva.
    * O botão é pressionado manualmente (nível LOW, devido à configuração pull-up) em qualquer momento, a bomba é desligada imediatamente, interrompendo a irrigação automática, caso esteja em andamento.

3.  **Estado da Bomba:**
    * Uma variável booleana (`bombaLigada`) rastreia o estado atual da bomba (ligada ou desligada).
    * O status da bomba (`on` ou `off`) é enviado para o servidor Python via HTTP.

## Código C/C++

O código C/C++ para o ESP32 lê os dados dos sensores, implementa a lógica de controle da bomba e envia os dados para o servidor Python. Os valores dos sensores também são exibidos localmente no display OLED. (O código completo está no arquivo `programa_esp32` na pasta src da entrega_1 do projeto).

## Próximos Passos (Entrega 2)

Na próxima entrega, os dados coletados e exibidos no monitor serial do ESP32 serão utilizados para simular o armazenamento em um banco de dados SQL usando um script Python, juntamente com a implementação das operações CRUD básicas.
