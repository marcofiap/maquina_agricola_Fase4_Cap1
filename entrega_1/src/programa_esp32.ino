// --- Bibliotecas para sensores e display LCD ---
#include <Adafruit_Sensor.h>
#include <DHT.h>                        // Biblioteca para sensor de temperatura e umidade DHT22
#include <Wire.h>
#include <LiquidCrystal_I2C.h>         // Biblioteca para display LCD2004

// --- Bibliotecas de comunicação Wi-Fi e HTTP ---
#include <WiFi.h>
#include <HTTPClient.h>                // Para enviar dados via HTTP GET

// --- Credenciais da rede Wi-Fi (usada no Wokwi) ---
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// --- Definição de pinos ---
#define BUTTON_FOSFORO 2              // Botão azul para simular sensor de fósforo
#define BUTTON_POTASSIO 18            // Botão amarelo para simular sensor de potássio
#define BUTTON_DESLIGAR_BOMBA 15      // Botão verde para desligar bomba manualmente
#define MODULORELEPIN 4               // Controle do relé (simula bomba de irrigação)
#define DHTPIN 5                       // Pino conectado ao sensor DHT22
#define DHTTYPE DHT22                 // Tipo do sensor de temperatura/umidade

// --- Inicializações ---
DHT dht(DHTPIN, DHTTYPE);             // Inicializa o DHT22
LiquidCrystal_I2C lcd(0x27, 20, 4);   // Inicializa o LCD (endereço I2C 0x27, 20 colunas, 4 linhas)

const int ldrPin = 34;                // Pino analógico para simular sensor de pH (via LDR)
int ldrValue = 0;                     // Valor lido do "sensor de pH"
bool bombaLigada = false;            // Estado atual da bomba

// --- Variáveis para controle de tempo ---
unsigned long ultimaLeituraDHT = 0;   // Última leitura do DHT
unsigned long ultimaLeituraLDR = 0;   // Última leitura do LDR
unsigned long ultimaAtualizacaoDisplay = 0; // Última atualização do display
unsigned long ultimoEnvioHTTP = 0;    // Último envio HTTP

// --- Intervalos de atualização (em ms) ---
const int INTERVALO_DHT = 2000;       // DHT22 requer no mínimo 2 segundos entre leituras
const int INTERVALO_LDR = 500;        // LDR pode ser lido mais frequentemente
const int INTERVALO_DISPLAY = 500;    // Atualização do display
const int INTERVALO_HTTP = 2000;      // Envio de dados para o servidor (2 segundos)

// --- Função para atualizar o display LCD ---
void atualizarDisplay(float t, float h, int phValue, String releStatus, String fosforo, String potassio) {
  if (millis() - ultimaAtualizacaoDisplay >= INTERVALO_DISPLAY) {
    ultimaAtualizacaoDisplay = millis();
    
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Temp ");
    lcd.print(t, 1);
    lcd.print("C Umd ");
    lcd.print(h, 1);
    lcd.print("%");
    
    lcd.setCursor(0, 1);
    lcd.print("pH: ");
    lcd.print(phValue);
    lcd.print("  Bomba: [");
    lcd.print(releStatus);
    lcd.print("]");
    
    lcd.setCursor(0, 2);
    lcd.print("Fosforo: [");
    lcd.print(fosforo);
    lcd.print("]");
    
    lcd.setCursor(0, 3);
    lcd.print("Potassio: [");
    lcd.print(potassio);
    lcd.print("]");
  }
}

// --- Função para enviar dados ao servidor ---
void enviarDadosServidor(float t, float h, int phValue, String fosforo, String potassio, String releStatus) {
  if (millis() - ultimoEnvioHTTP >= INTERVALO_HTTP) {
    ultimoEnvioHTTP = millis();
    
    String sensorData = "umidade=" + String(h) + "&temperatura=" + String(t) +
                       "&ph=" + String(phValue) + "&fosforo=" + fosforo +
                       "&potassio=" + potassio + "&rele=" + releStatus;

    String serverAddress = "http://192.168.0.12:8000/data?" + sensorData;

    WiFiClient client;
    HTTPClient http;
    http.begin(client, serverAddress);
    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
      String response = http.getString();
      Serial.println("Response from server: " + response);
    } else {
      Serial.println("Erro na requisição HTTP: ");
      Serial.println(http.errorToString(httpResponseCode));
    }
    http.end();
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
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi conectado!");
  Serial.println(WiFi.localIP());

  // Inicializa o display LCD
  lcd.init();
  lcd.backlight();                    // Liga o LED de fundo
}

// --- Loop principal ---
void loop() {
  unsigned long tempoAtual = millis();
  
  // --- Leitura dos sensores P e K (simulados por botões) ---
  int buttonPState = digitalRead(BUTTON_FOSFORO);
  int buttonKState = digitalRead(BUTTON_POTASSIO);
  String fosforo = (buttonPState == LOW) ? "presente" : "ausente";
  String potassio = (buttonKState == LOW) ? "presente" : "ausente";

  // --- Leitura do DHT22 ---
  static float t = 0, h = 0;
  if (tempoAtual - ultimaLeituraDHT >= INTERVALO_DHT) {
    ultimaLeituraDHT = tempoAtual;
    h = dht.readHumidity();
    t = dht.readTemperature();
  }

  // --- Leitura do LDR (pH) ---
  static int phValue = 0;
  if (tempoAtual - ultimaLeituraLDR >= INTERVALO_LDR) {
    ultimaLeituraLDR = tempoAtual;
    ldrValue = analogRead(ldrPin);
    phValue = ldrValue / 290;
  }

  // --- Lógica para controle do relé (irrigação) ---
  bool mostrarIrrigacao = (h < 40.0);
  int botaoDesligarState = digitalRead(BUTTON_DESLIGAR_BOMBA);

  int controleBombaEstado;
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

  String releStatus = bombaLigada ? "on" : "off";

  // --- Atualização do display LCD ---
  atualizarDisplay(t, h, phValue, releStatus, fosforo, potassio);

  // --- Envio de dados ao servidor ---
  enviarDadosServidor(t, h, phValue, fosforo, potassio, releStatus);
}



