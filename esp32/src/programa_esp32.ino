// --- Bibliotecas para sensores e display LCD ---
#include <Adafruit_Sensor.h>
#include <DHT.h>                        // Biblioteca para sensor de temperatura e umidade DHT22
#include <Wire.h>
#include <LiquidCrystal_I2C.h>         // Biblioteca para display LCD2004

// --- Bibliotecas de comunicação Wi-Fi e HTTP ---
#include <WiFi.h>
#include <HTTPClient.h>                // Para enviar dados via HTTP GET
#include <time.h>                      // Biblioteca para sincronização de tempo via NTP

// --- Credenciais da rede Wi-Fi (usada no Wokwi) ---
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// --- Configurações de NTP (Servidor de tempo) ---
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = -3 * 3600;    // GMT-3 (horário de Brasília)
const int daylightOffset_sec = 0;         // Sem horário de verão
bool ntpSincronizado = false;

// --- Definição de pinos ---
#define BUTTON_FOSFORO 2              // Botão azul para simular sensor de fósforo
#define BUTTON_POTASSIO 18            // Botão amarelo para simular sensor de potássio
#define BUTTON_DESLIGAR_BOMBA 15      // Botão verde para desligar bomba manualmente
#define MODULORELEPIN 4               // Controle do relé (simula bomba de irrigação)
#define DHTPIN 5                       // Pino conectado ao sensor DHT22
#define DHTTYPE DHT22                 // Tipo do sensor de temperatura/umidade
#define LDR_PIN 34                    // OTIMIZAÇÃO: Definido como macro para economizar RAM

// --- Inicializações ---
DHT dht(DHTPIN, DHTTYPE);             // Inicializa o DHT22
LiquidCrystal_I2C lcd(0x27, 20, 4);   // Inicializa o LCD (endereço I2C 0x27, 20 colunas, 4 linhas)

// OTIMIZAÇÃO: Usando uint32_t para valores analógicos altos
uint32_t ldrValue = 0;                // Valor lido do "sensor de pH"
bool bombaLigada = false;             // Estado atual da bomba

// --- Variáveis para controle de tempo ---
uint32_t ultimaLeituraDHT = 0;        // Última leitura do DHT
uint32_t ultimaLeituraLDR = 0;        // Última leitura do LDR
uint32_t ultimaAtualizacaoDisplay = 0; // Última atualização do display
uint32_t ultimoEnvioHTTP = 0;         // Último envio HTTP

// OTIMIZAÇÃO: Variáveis para reutilização de conexão HTTP
static WiFiClient httpClient;
static HTTPClient http;
static bool httpInicializado = false;

// --- Intervalos de atualização (em ms) ---
// OTIMIZAÇÃO: Reduzidos os intervalos para melhor responsividade dos sensores
const uint16_t INTERVALO_DHT = 1000;       // DHT22: reduzido de 2000ms para 1000ms (mínimo seguro)
const uint16_t INTERVALO_LDR = 100;        // LDR: reduzido de 500ms para 100ms (muito mais responsivo)
const uint16_t INTERVALO_DISPLAY = 50;     // Display: reduzido de 200ms para 50ms (atualização muito mais fluida)
const uint16_t INTERVALO_HTTP = 1000;      // HTTP: reduzido de 2000ms para 1000ms (atualizações mais frequentes)

// OTIMIZAÇÃO: Strings constantes para reduzir uso de memória heap
const char* STR_TEMP = "Temp ";
const char* STR_C = "C Umd ";
const char* STR_PERCENT = "%";
const char* STR_PH = "pH: ";
const char* STR_BOMBA = "  Bomba: [";
const char* STR_FOSFORO = "Fosforo: [";
const char* STR_POTASSIO = "Potassio: [";
const char* STR_PRESENTE = "presente";
const char* STR_AUSENTE = "ausente";
const char* STR_ON = "on";
const char* STR_OFF = "off";

// --- Função para atualizar o display LCD ---
void atualizarDisplay(float t, float h, uint8_t phValue, const char* releStatus, const char* fosforo, const char* potassio) {
  if (millis() - ultimaAtualizacaoDisplay >= INTERVALO_DISPLAY) {
    ultimaAtualizacaoDisplay = millis();
    
    // OTIMIZAÇÃO: Limpa apenas uma vez e usa setCursor de forma mais eficiente
    lcd.clear();
    
    // Linha 1: Temperatura e Umidade
    lcd.setCursor(0, 0);
    lcd.print(STR_TEMP);
    lcd.print(t, 1);
    lcd.print(STR_C);
    lcd.print(h, 1);
    lcd.print(STR_PERCENT);
    
    // Linha 2: pH e Status da Bomba
    lcd.setCursor(0, 1);
    lcd.print(STR_PH);
    lcd.print(phValue);
    lcd.print(STR_BOMBA);
    lcd.print(releStatus);
    lcd.print("]");
    
    // Linha 3: Fósforo
    lcd.setCursor(0, 2);
    lcd.print(STR_FOSFORO);
    lcd.print(fosforo);
    lcd.print("]");
    
    // Linha 4: Potássio
    lcd.setCursor(0, 3);
    lcd.print(STR_POTASSIO);
    lcd.print(potassio);
    lcd.print("]");
  }
}

// --- Função para obter timestamp formatado ---
String obterTimestamp() {
  struct tm timeinfo;
  if(!getLocalTime(&timeinfo)){
    Serial.println("Falha ao obter timestamp - usando millis()");
    // Fallback: usa millis() se NTP não funcionar
    uint32_t segundos = millis() / 1000;
    uint32_t minutos = segundos / 60;
    uint32_t horas = minutos / 60;
    segundos = segundos % 60;
    minutos = minutos % 60;
    horas = horas % 24;
    
    char buffer[20];
    snprintf(buffer, sizeof(buffer), "2024-01-01T%02d:%02d:%02d", 
             (int)horas, (int)minutos, (int)segundos);
    return String(buffer);
  }
  
  // Formata timestamp no padrão ISO: YYYY-MM-DDTHH:MM:SS (sem espaços)
  char buffer[20];
  strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%S", &timeinfo);
  return String(buffer);
}

// --- Array de servidores para envio de dados ---
const char* servidores[] = {
  "192.168.0.13:8000",
  "192.168.2.126:8000"
};
const uint8_t NUM_SERVIDORES = sizeof(servidores) / sizeof(servidores[0]);

// --- Função para enviar dados ao servidor ---
void enviarDadosServidor(float t, float h, uint8_t phValue, const char* fosforo, const char* potassio, const char* releStatus) {
  if (millis() - ultimoEnvioHTTP >= INTERVALO_HTTP) {
    ultimoEnvioHTTP = millis();
    
    // OTIMIZAÇÃO: Verifica se Wi-Fi está conectado antes de tentar enviar
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("Wi-Fi desconectado - pulando envio HTTP");
      return;
    }
    
    // OTIMIZAÇÃO: Inicializa HTTP apenas uma vez
    if (!httpInicializado) {
      http.setTimeout(3000); // 3 segundos de timeout
      httpInicializado = true;
    }
    
    // OTIMIZAÇÃO: Tenta enviar para cada servidor no array
    bool envioSucesso = false;
    
    // Obtém timestamp atual para esta leitura
    String timestamp = obterTimestamp();
    
    for (uint8_t i = 0; i < NUM_SERVIDORES && !envioSucesso; i++) {
      // OTIMIZAÇÃO: Usando snprintf em vez de concatenação de String para economizar heap
      char urlBuffer[300]; // Buffer aumentado para incluir timestamp
      snprintf(urlBuffer, sizeof(urlBuffer), 
               "http://%s/data?timestamp=%s&umidade=%.1f&temperatura=%.1f&ph=%d&fosforo=%s&potassio=%s&rele=%s",
               servidores[i], timestamp.c_str(), h, t, phValue, fosforo, potassio, releStatus);

      Serial.print("Tentando servidor [");
      Serial.print(i + 1);
      Serial.print("/");
      Serial.print(NUM_SERVIDORES);
      Serial.print("]: ");
      Serial.println(servidores[i]);
      Serial.print("Timestamp: ");
      Serial.println(timestamp);

      // OTIMIZAÇÃO: Reutiliza a conexão HTTP
      http.begin(httpClient, urlBuffer);
      
      int httpResponseCode = http.GET();

      if (httpResponseCode > 0) {
        // OTIMIZAÇÃO: Não lê a resposta completa se não for necessário
        if (httpResponseCode == 200) {
          Serial.print("HTTP OK [");
          Serial.print(servidores[i]);
          Serial.print("]: ");
          Serial.println(httpResponseCode);
          envioSucesso = true;
        } else {
          Serial.print("HTTP Response [");
          Serial.print(servidores[i]);
          Serial.print("]: ");
          Serial.println(httpResponseCode);
          // Só lê a resposta se houver erro
          String response = http.getString();
          Serial.println("Response: " + response);
        }
      } else {
        Serial.print("HTTP Error [");
        Serial.print(servidores[i]);
        Serial.print("]: ");
        Serial.println(http.errorToString(httpResponseCode));
      }
      
      // OTIMIZAÇÃO: Fecha a conexão imediatamente
      http.end();
      
      // Se não conseguiu enviar, aguarda um pouco antes de tentar o próximo
      if (!envioSucesso && i < NUM_SERVIDORES - 1) {
        delay(500); // 500ms entre tentativas
      }
    }
    
    if (envioSucesso) {
      Serial.println("Dados enviados com sucesso!");
    } else {
      Serial.println("Falha ao enviar para todos os servidores");
    }
  }
}

// --- Função de inicialização ---
void setup() {
  Serial.begin(115200);               // Inicia comunicação serial
  Serial.println("Iniciando sensores e componentes...");

  // Define botões como entrada com pull-up interno
  pinMode(BUTTON_FOSFORO, INPUT_PULLUP);
  pinMode(BUTTON_POTASSIO, INPUT_PULLUP);
  pinMode(BUTTON_DESLIGAR_BOMBA, INPUT_PULLUP);
  pinMode(MODULORELEPIN, OUTPUT);    // Pino do relé como saída
  dht.begin();                        // Inicia o sensor DHT

  // Conecta ao Wi-Fi
  WiFi.begin(ssid, password, 6);      // Conexão com rede Wokwi
  
  // OTIMIZAÇÃO: Timeout na conexão Wi-Fi para evitar travamentos
  uint8_t tentativasWiFi = 0;
  const uint8_t MAX_TENTATIVAS_WIFI = 20; // 10 segundos máximo
  
  while (WiFi.status() != WL_CONNECTED && tentativasWiFi < MAX_TENTATIVAS_WIFI) {
    delay(500);
    Serial.print(".");
    tentativasWiFi++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWi-Fi conectado!");
    Serial.println(WiFi.localIP());
    
    // Configura sincronização de tempo via NTP
    Serial.println("Configurando NTP...");
    configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
    
    // Aguarda sincronização (até 10 segundos)
    struct tm timeinfo;
    uint8_t tentativasNTP = 0;
    while(!getLocalTime(&timeinfo) && tentativasNTP < 20) {
      delay(500);
      Serial.print(".");
      tentativasNTP++;
    }
    
    if (getLocalTime(&timeinfo)) {
      ntpSincronizado = true;
      Serial.println("\nNTP sincronizado!");
      Serial.print("Data/Hora atual: ");
      Serial.println(obterTimestamp());
    } else {
      Serial.println("\nFalha na sincronização NTP - continuando sem timestamp real");
    }
  } else {
    Serial.println("\nFalha na conexão Wi-Fi - continuando sem rede");
  }

  // Inicializa o display LCD
  lcd.init();
  lcd.backlight();                    // Liga o LED de fundo
}

// --- Loop principal ---
void loop() {
  uint32_t tempoAtual = millis();
  
  // --- Leitura dos sensores P e K (simulados por botões) ---
  uint8_t buttonPState = digitalRead(BUTTON_FOSFORO);
  uint8_t buttonKState = digitalRead(BUTTON_POTASSIO);
  const char* fosforo = (buttonPState == LOW) ? STR_PRESENTE : STR_AUSENTE;
  const char* potassio = (buttonKState == LOW) ? STR_PRESENTE : STR_AUSENTE;
  
  // OTIMIZAÇÃO: Detecta mudanças nos botões para forçar atualização do display
  static uint8_t buttonPState_anterior = HIGH;
  static uint8_t buttonKState_anterior = HIGH;
  bool botaoMudou = (buttonPState != buttonPState_anterior) || (buttonKState != buttonKState_anterior);
  buttonPState_anterior = buttonPState;
  buttonKState_anterior = buttonKState;

  // --- Leitura do DHT22 ---
  static float t = 0, h = 0;
  bool dadosDHTAtualizados = false;
  if (tempoAtual - ultimaLeituraDHT >= INTERVALO_DHT) {
    ultimaLeituraDHT = tempoAtual;
    
    // OTIMIZAÇÃO: Leitura mais eficiente do DHT22 com verificação de erro
    float novaTemperatura = dht.readTemperature();
    float novaUmidade = dht.readHumidity();
    
    // Só atualiza se a leitura foi bem-sucedida (não é NaN)
    if (!isnan(novaTemperatura) && !isnan(novaUmidade)) {
      t = novaTemperatura;
      h = novaUmidade;
      dadosDHTAtualizados = true;
      
      // Debug DHT22
      Serial.println("\n=== Leitura DHT22 ===");
      Serial.print("Temperatura: ");
      Serial.print(t);
      Serial.print("°C | Umidade: ");
      Serial.print(h);
      Serial.println("%");
    } else {
      Serial.println("Falha na leitura do DHT22!");
    }
  }

  // --- Leitura do LDR (pH) ---
  static uint8_t phValue = 0;
  bool dadosLDRAtualizados = false;
  
  if (tempoAtual - ultimaLeituraLDR >= INTERVALO_LDR) {
    ultimaLeituraLDR = tempoAtual;
    
    // OTIMIZAÇÃO: Leitura direta do LDR sem média móvel
    ldrValue = analogRead(LDR_PIN);
    uint8_t phAnterior = phValue;
    
    // Calcula pH diretamente baseado na tabela de conversão
    Serial.println("\n=== Leitura LDR/pH ===");
    Serial.print("Valor LDR bruto: ");
    Serial.println(ldrValue);
    
    // Ajuste do mapeamento do LDR para pH
    // Valores do LDR no ESP32 vão de 0 a 4095
    // Dividimos em 5 faixas para os valores de pH (5 a 9)
    const uint16_t FAIXA_LDR = 4095 / 5; // Aproximadamente 819 por faixa
    
    if (ldrValue < FAIXA_LDR) {
      phValue = 5; // Muito ácido
      Serial.println("Faixa: 0-819 (pH 5 - muito ácido)");
    } else if (ldrValue < FAIXA_LDR * 2) {
      phValue = 6; // Ácido
      Serial.println("Faixa: 820-1638 (pH 6 - ácido)");
    } else if (ldrValue < FAIXA_LDR * 3) {
      phValue = 7; // Neutro
      Serial.println("Faixa: 1639-2457 (pH 7 - neutro)");
    } else if (ldrValue < FAIXA_LDR * 4) {
      phValue = 8; // Básico
      Serial.println("Faixa: 2458-3276 (pH 8 - básico)");
    } else {
      phValue = 9; // Muito básico
      Serial.println("Faixa: 3277-4095 (pH 9 - muito básico)");
    }
    
    Serial.print("pH final: ");
    Serial.println(phValue);
    
    dadosLDRAtualizados = (phValue != phAnterior);
  }

  // --- Lógica para controle do relé (irrigação) ---
  bool mostrarIrrigacao = (h < 40.0);
  uint8_t botaoDesligarState = digitalRead(BUTTON_DESLIGAR_BOMBA);
  static bool bombaLigada_anterior = bombaLigada;

  // Debug estado da bomba
  if (botaoDesligarState == LOW || mostrarIrrigacao != bombaLigada) {
    Serial.println("\n=== Estado da Bomba ===");
    Serial.print("Umidade atual: ");
    Serial.print(h);
    Serial.print("% | Limite: 40.0% | Botão desligar: ");
    Serial.println(botaoDesligarState == LOW ? "Pressionado" : "Solto");
  }

  uint8_t controleBombaEstado;
  if (botaoDesligarState == LOW) {
    controleBombaEstado = 2; // Chuva detectada (manual OFF)
  } else if (mostrarIrrigacao) {
    controleBombaEstado = 1; // Umidade baixa (ligar bomba)
  } else {
    controleBombaEstado = 0; // Umidade OK (desliga bomba)
  }

  switch (controleBombaEstado) {
    case 0:
      digitalWrite(MODULORELEPIN, LOW);
      bombaLigada = false;
      break;
    case 1:
      digitalWrite(MODULORELEPIN, HIGH);
      bombaLigada = true;
      break;
    case 2:
      digitalWrite(MODULORELEPIN, LOW);
      bombaLigada = false;
      break;
    default:
      digitalWrite(MODULORELEPIN, LOW);
      bombaLigada = false;
      break;
  }

  const char* releStatus = bombaLigada ? STR_ON : STR_OFF;
  
  // Debug mudança de estado da bomba
  if (bombaLigada != bombaLigada_anterior) {
    Serial.print("Bomba: ");
    Serial.println(bombaLigada ? "LIGADA" : "DESLIGADA");
  }
  
  bool bombaMudou = (bombaLigada != bombaLigada_anterior);
  bombaLigada_anterior = bombaLigada;

  // --- Atualização do display LCD ---
  // OTIMIZAÇÃO: Força atualização do display quando há novos dados dos sensores
  if (dadosDHTAtualizados || dadosLDRAtualizados || botaoMudou || bombaMudou) {
    ultimaAtualizacaoDisplay = 0; // Força atualização imediata
  }
  atualizarDisplay(t, h, phValue, releStatus, fosforo, potassio);

  // --- Envio de dados ao servidor ---
  enviarDadosServidor(t, h, phValue, fosforo, potassio, releStatus);
}