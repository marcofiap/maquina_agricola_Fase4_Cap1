# Sistema de Irrigação Inteligente com ESP32  
### Projeto Fase 3 – FarmTech Solutions | FIAP

Este projeto simula um sistema de irrigação automatizado utilizando o microcontrolador ESP32, sensores físicos (ou simulados) e lógica de controle embarcada. Desenvolvido no simulador Wokwi, o sistema integra leitura de sensores, acionamento de bomba via relé e visualização de dados em um display OLED.

Além disso, os dados dos sensores são enviados via HTTP a um backend Python que registra as informações em um banco SQL e permite visualização futura via dashboard. A lógica permite controle automático da irrigação com base na umidade do solo e também controle **manual** em caso de **previsão de chuva**, com base em dados de uma **API climática**.

---

## Índice

- [Grupo](#grupo)
- [Visão Geral](#visão-geral-do-projeto)
- [Circuito Wokwi](#circuito-wokwi)
- [Componentes](#componentes-utilizados)
- [Conexões](#conexões)
- [Lógica de Controle](#lógica-de-controle-da-bomba-de-irrigação)
- [Código](#código-cc)
- [Otimizações de Memória](#🚀-otimizações-de-memória)
- [IP Local no Código](#️configuração-do-endereço-ip-no-codigo-do-esp32)

---

## Grupo

**Grupo 65 – FIAP**  
*Integrantes:*
- Felipe Sabino da Silva  
- Juan Felipe Voltolini  
- Luiz Henrique Ribeiro de Oliveira  
- Marco Aurélio Eberhardt Assimpção  
- Paulo Henrique Senise  

*Professores:*  
- Tutor: Leonardo Ruiz Orabona  
- Coordenador: André Godoi

---

## Visão Geral do Projeto

O sistema realiza:
- Leitura da **umidade do solo**, **pH**, **fósforo** e **potássio**.
- Acionamento automático da bomba quando a umidade está abaixo do ideal.
- Controle manual da irrigação por botão físico em caso de previsão de chuva.
- Exibição local dos dados no **display OLED**.
- Envio dos dados via **HTTP GET** para armazenamento em banco SQL.

---

## Circuito Wokwi

O projeto foi montado e testado no simulador online [Wokwi](https://wokwi.com). As imagens abaixo mostram os sensores e botões simulados em ação:


- LDR é um sensor eletrônico
- DHT22 é um sensor eletrônico
- Botões(amarelo e azul) pushbotom
- Botão(verde) pushbotom
- Relé simulado por LED vermelho 
- Display OLED 

---

## Componentes Utilizados

| Componente        | Função                                    |
|-------------------|-------------------------------------------|
| **ESP32**         | Microcontrolador principal                |
| **DHT22**         | Sensor de temperatura e umidade           |
| **LDR**           | Simula leitura de pH                      |
| **Botões (2)**    | Simulam sensores de Fósforo e Potássio    |
| **Botão (15)**    | Desligar manualmente a bomba              |
| **Display OLED**  | Exibe dados locais                        |
| **Relé (LED)**    | Simula bomba de irrigação                 |

---

## Imagens do Projeto Eletrônico

- Detalhes individuais dos componentes utilizados no circuito simulador wokwi.
![ComponentesEletronicos](https://github.com/user-attachments/assets/d4cb7f36-a7ce-4803-af37-cd8949f2ffbd)

- Visão geral do projeto montado.

![CircuitoMontadoSimulador](https://github.com/user-attachments/assets/7d1bc44a-0881-43e7-bbf6-208411a68dbc)

---

## Conexões

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

## Lógica de Controle da Bomba de Irrigação

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

> Caso deseje ver a visualização dos dados e integração com banco/API, acesse as outras entregas na pasta raiz do projeto.

## Código C/C++

O código responsável pela leitura dos sensores, lógica de irrigação e comunicação com o servidor está disponível na pasta:

  [Código do ESP32 – programa_esp32.ino](./src/programa_esp32.ino)

- Os valores dos sensores são exibidos localmente no **display OLED**.
- Dados são enviados via `HTTP GET` para o servidor Flask.
- Todas as leituras são visíveis no **Serial Monitor**.

---

## 🚀 Otimizações de Memória

O código foi otimizado para maximizar a eficiência de memória no ESP32, garantindo melhor performance e estabilidade do sistema.

### **Principais Otimizações Implementadas:**

#### **1. Tipos de Dados Otimizados**
```cpp
// Antes: int (4 bytes) → Depois: uint8_t (1 byte)
uint8_t buttonPState = digitalRead(BUTTON_FOSFORO);
uint8_t phValue = 0;

// Antes: int (4 bytes) → Depois: uint16_t (2 bytes)  
uint16_t ldrValue = 0;

// Antes: unsigned long (4 bytes) → Depois: uint32_t (4 bytes, mais eficiente)
uint32_t ultimaLeituraDHT = 0;
```

#### **2. Constantes e Macros**
```cpp
// OTIMIZAÇÃO: Usando #define em vez de const int para economizar RAM
#define LDR_PIN 34

// OTIMIZAÇÃO: Usando uint16_t para intervalos (0-65535 ms é suficiente)
const uint16_t INTERVALO_DHT = 2000;
```

#### **3. Otimização de Strings**
```cpp
// OTIMIZAÇÃO: Strings constantes para reduzir uso de memória heap
const char* STR_TEMP = "Temp ";
const char* STR_PRESENTE = "presente";
const char* STR_AUSENTE = "ausente";

// OTIMIZAÇÃO: Usando snprintf em vez de concatenação de String
char urlBuffer[256];
snprintf(urlBuffer, sizeof(urlBuffer), 
         "http://192.168.0.12:8000/data?umidade=%.1f&temperatura=%.1f&ph=%d&fosforo=%s&potassio=%s&rele=%s",
         h, t, phValue, fosforo, potassio, releStatus);
```

#### **4. Variáveis Estáticas e Ponteiros**
```cpp
// OTIMIZAÇÃO: Usando static para manter valores entre chamadas
static uint8_t phValue = 0;

// OTIMIZAÇÃO: Ponteiros para strings constantes em vez de criar novas Strings
const char* fosforo = (buttonPState == LOW) ? STR_PRESENTE : STR_AUSENTE;
```

#### **5. Timeout na Conexão Wi-Fi**
```cpp
// OTIMIZAÇÃO: Evita travamentos na conexão Wi-Fi
uint8_t tentativasWiFi = 0;
const uint8_t MAX_TENTATIVAS_WIFI = 20; // 10 segundos máximo

while (WiFi.status() != WL_CONNECTED && tentativasWiFi < MAX_TENTATIVAS_WIFI) {
  delay(500);
  tentativasWiFi++;
}
```

#### **6. Atualização Inteligente do Display**
```cpp
// OTIMIZAÇÃO: Só atualiza quando há mudanças reais nos dados
static float t_anterior = -999;
static float h_anterior = -999;
static uint8_t ph_anterior = 255;

bool dadosMudaram = (abs(t - t_anterior) > 0.1) || 
                   (abs(h - h_anterior) > 0.1) || 
                   (phValue != ph_anterior);

if (dadosMudaram) {
  // Atualiza o display apenas quando necessário
  lcd.clear();
  // ... resto da atualização
}
```

#### **7. Otimizações de Conexão HTTP/Banco de Dados**
```cpp
// OTIMIZAÇÃO: Reutilização de conexão HTTP
static WiFiClient httpClient;
static HTTPClient http;
static bool httpInicializado = false;

// OTIMIZAÇÃO: Timeout reduzido para conexão mais rápida
http.setTimeout(3000); // 3 segundos em vez do padrão

// OTIMIZAÇÃO: Verificação de Wi-Fi antes de enviar
if (WiFi.status() != WL_CONNECTED) {
  return; // Pula envio se não há conexão
}

// OTIMIZAÇÃO: Não lê resposta completa se sucesso
if (httpResponseCode == 200) {
  Serial.print("HTTP OK: ");
  Serial.println(httpResponseCode);
} else {
  // Só lê resposta em caso de erro
  String response = http.getString();
}
```

#### **8. Correção da Lógica de Medição do pH**
```cpp
// ANTES (incorreto):
phValue = ldrMedia / 290;  // Resultava em valores estranhos

// DEPOIS (correto):
// Leitura direta do LDR sem média móvel
ldrValue = analogRead(LDR_PIN);

// Calcula pH diretamente baseado na tabela de conversão
if (ldrValue <= 1000) {
  phValue = map(ldrValue, 0, 1000, 5, 6);
} else if (ldrValue <= 2000) {
  phValue = map(ldrValue, 1000, 2000, 6, 7);
} else if (ldrValue <= 3000) {
  phValue = map(ldrValue, 2000, 3000, 7, 8);
} else if (ldrValue <= 3500) {
  phValue = map(ldrValue, 3000, 3500, 8, 9);
} else {
  phValue = 9; // Máximo para valores acima de 3500
}

phValue = constrain(phValue, 5, 9);

// DEBUG para calibração:
Serial.print("LDR: ");
Serial.print(ldrValue);
Serial.print(" | pH: ");
Serial.println(phValue);
```

### **Escala de pH Corrigida (Solo Agrícola):**

| Condição do LDR  | Valor LDR | pH Resultante | Classificação do Solo |
|------------------|-----------|---------------|-----------------------|
| **Muito escuro** | 0-819     |       5       | Muito ácido           |
| **Escuro**       | 820-1638  |       6       | Ácido                 |
| **Meio termo**   | 1639-2457 |       7       | Neutro                |
| **Claro**        | 2458-3276 |       8       | Básico                |
| **Muito claro**  | 3277-4095 |       9       | Muito básico          |

### **Benefícios da Correção do pH:**

✅ **pH sempre entre 5-9** - Escala correta para solo agrícola  
✅ **Leitura direta** - Sem média móvel, resposta instantânea  
✅ **Mapeamento por faixas** - Conversão precisa baseada na tabela  
✅ **Debug simplificado** - Mostra LDR e pH diretamente  
✅ **Proteção contra valores inválidos** - Sempre entre 5-9  
✅ **Resposta rápida** - Atualização a cada 100ms

### **Economia de Memória Estimada:**

| Otimização | Antes | Depois | Economia |
|------------|-------|--------|----------|
| `int` → `uint8_t` | 4 bytes | 1 byte | **3 bytes** |
| `int` → `uint16_t` | 4 bytes | 2 bytes | **2 bytes** |
| Strings dinâmicas → `const char*` | ~50-100 bytes | ~10 bytes | **~40-90 bytes** |
| Concatenação String → `snprintf` | ~200 bytes | ~256 bytes fixo | **Evita fragmentação** |

### **Benefícios das Otimizações:**

✅ **Menor uso de RAM** - Especialmente importante no ESP32  
✅ **Menos fragmentação de heap** - Evita criação/destruição de Strings  
✅ **Execução mais rápida** - Tipos menores = menos operações de memória  
✅ **Código mais previsível** - Buffer fixo para URL HTTP  
✅ **Melhor estabilidade** - Menos alocações dinâmicas

### **🚀 Otimizações de Performance (Velocidade de Leitura):**

Além das otimizações de memória, implementamos melhorias específicas para **aumentar a responsividade dos sensores**:

#### **1. Intervalos de Leitura Otimizados**
```cpp
// ANTES (lento):
const uint16_t INTERVALO_DHT = 2000;       // 2 segundos
const uint16_t INTERVALO_LDR = 500;        // 500ms
const uint16_t INTERVALO_DISPLAY = 500;    // 500ms

// DEPOIS (rápido):
const uint16_t INTERVALO_DHT = 1000;       // 1 segundo (mínimo seguro)
const uint16_t INTERVALO_LDR = 100;        // 100ms (5x mais rápido)
const uint16_t INTERVALO_DISPLAY = 50;     // 50ms (10x mais rápido!)
```

#### **2. Leitura Inteligente do DHT22**
```cpp
// OTIMIZAÇÃO: Verificação de erro para evitar valores NaN
float novaTemperatura = dht.readTemperature();
float novaUmidade = dht.readHumidity();

if (!isnan(novaTemperatura)) {
  t = novaTemperatura;
}
if (!isnan(novaUmidade)) {
  h = novaUmidade;
}
```

#### **3. Média Móvel para LDR (Estabilização)**
```cpp
// OTIMIZAÇÃO: Média móvel simples para estabilizar leitura
ldrValue = analogRead(LDR_PIN);
ldrSoma += ldrValue;
ldrContador++;

if (ldrContador >= 5) {
  uint16_t ldrMedia = ldrSoma / ldrContador;
  phValue = ldrMedia / 290;
  ldrSoma = 0;
  ldrContador = 0;
}
```

#### **4. Timeout na Conexão Wi-Fi**
```cpp
// OTIMIZAÇÃO: Evita travamentos na conexão Wi-Fi
uint8_t tentativasWiFi = 0;
const uint8_t MAX_TENTATIVAS_WIFI = 20; // 10 segundos máximo

while (WiFi.status() != WL_CONNECTED && tentativasWiFi < MAX_TENTATIVAS_WIFI) {
  delay(500);
  tentativasWiFi++;
}
```

#### **5. Atualização Inteligente do Display**
```cpp
// OTIMIZAÇÃO: Só atualiza quando há mudanças reais nos dados
static float t_anterior = -999;
static float h_anterior = -999;
static uint8_t ph_anterior = 255;

bool dadosMudaram = (abs(t - t_anterior) > 0.1) || 
                   (abs(h - h_anterior) > 0.1) || 
                   (phValue != ph_anterior);

if (dadosMudaram) {
  // Atualiza o display apenas quando necessário
  lcd.clear();
  // ... resto da atualização
}
```

### **Melhorias de Performance:**

⚡ **LDR 5x mais rápido** - De 500ms para 100ms  
⚡ **Display 10x mais responsivo** - De 500ms para 50ms  
⚡ **DHT22 2x mais rápido** - De 2000ms para 1000ms  
⚡ **HTTP 2x mais frequente** - De 2000ms para 1000ms  
⚡ **Leituras mais estáveis** - Média móvel no LDR  
⚡ **Conexão Wi-Fi mais confiável** - Timeout de 10 segundos  
⚡ **Display inteligente** - Só atualiza quando há mudanças  
⚡ **Conexão HTTP otimizada** - Timeout de 3s e reutilização

### **Comentários no Código:**
Cada otimização está comentada com `// OTIMIZAÇÃO:` explicando a razão da mudança, facilitando a manutenção e compreensão do código.

---

## Configuração do Endereço IP no Código do ESP32

Para que o **ESP32** consiga enviar dados ao servidor Python (`serve.py`), é necessário informar o **endereço IP local da máquina** onde o servidor está rodando.

No código do ESP32, existe uma linha como esta:

```cpp
// --- Monta string para envio ao servidor Flask/Python ---
  String sensorData = "umidade=" + String(h) + "&temperatura=" + String(t) +
                      "&ph=" + String(phValue) + "&fosforo=" + fosforo +
                      "&potassio=" + potassio + "&rele=" + releStatus;

  String serverAddress = "http://192.168.0.12:8000/data?" + sensorData;
```

Você deve substituir o IP `192.168.0.12` pelo **seu IP local** (da máquina que roda o Flask), garantindo que o ESP32 e o servidor estejam na **mesma rede**.

### Como descobrir seu IP local (Windows):

1. Abra o **Prompt de Comando** (`cmd`)  
2. Digite o comando: `ipconfig`  
3. Localize o campo: `Endereço IPv4` (exemplo: `192.168.0.15`)

### Exemplo atualizado no código:

```cpp
String serverAddress = "http://192.168.0.15:8000/data?" + sensorData;
```

Com isso, o envio de dados para o backend funcionará corretamente via `HTTP GET.




