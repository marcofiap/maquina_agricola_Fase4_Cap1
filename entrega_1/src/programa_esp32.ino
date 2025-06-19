// --- Bibliotecas para sensores e display OLED ---
#include <Adafruit_Sensor.h>
#include <DHT.h>                        // Biblioteca para sensor de temperatura e umidade DHT22
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>          // Biblioteca para display OLED

// --- Bibliotecas de comunicação Wi-Fi e HTTP ---
#include <WiFi.h>
#include <HTTPClient.h>                // Para enviar dados via HTTP GET

// --- Bibliotecas para data/hora ---
#include <time.h>                      // Para funções de tempo
#include <WiFiUdp.h>                   // Para sincronização NTP

// --- Credenciais da rede Wi-Fi (usada no Wokwi) ---
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// --- Definição de pinos ---
#define BUTTON1 2                      // Botão para simular sensor de fósforo
#define BUTTON2 18                     // Botão para simular sensor de potássio
#define BUTTON_DESLIGAR_BOMBA 15      // Botão manual para desligar bomba (chuva)
#define MODULORELEPIN 4               // Controle do relé (simula bomba de irrigação)
#define DHTPIN 5                       // Pino conectado ao sensor DHT22
#define DHTTYPE DHT22                 // Tipo do sensor de temperatura/umidade

// --- Configurações do display OLED ---
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1

// --- Inicializações ---
DHT dht(DHTPIN, DHTTYPE);             // Inicializa o DHT22
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

const int ldrPin = 34;                // Pino analógico para simular sensor de pH (via LDR)
int ldrValue = 0;                     // Valor lido do "sensor de pH"
bool bombaLigada = false;            // Estado atual da bomba

// --- Configurações NTP para timestamp ---
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = -3 * 3600;  // GMT-3 (Brasília)
const int daylightOffset_sec = 0;      // Sem horário de verão

// --- Função para obter timestamp formatado ---
String getFormattedDateTime() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("❌ Falha ao obter hora do NTP");
    return "1970-01-01 00:00:00"; // Fallback para epoch
  }
  
  char dateTimeString[20];
  strftime(dateTimeString, sizeof(dateTimeString), "%Y-%m-%d %H:%M:%S", &timeinfo);
  return String(dateTimeString);
}

// --- Função para codificar URL (substitui espaços por %20) ---
String urlEncode(String str) {
  str.replace(" ", "%20");
  return str;
}

// --- Função para exibir data/hora no Serial ---
void printDateTime() {
  struct tm timeinfo;
  if (getLocalTime(&timeinfo)) {
    Serial.print("🕐 Data/Hora atual: ");
    Serial.println(getFormattedDateTime());
  }
}

// --- Função de inicialização ---
void setup() {
  Serial.begin(115200);               // Inicia comunicação serial
  Serial.println("Iniciando sensores e componentes...");

  // Define botões como entrada com pull-up interno
  pinMode(BUTTON1, INPUT_PULLUP);
  pinMode(BUTTON2, INPUT_PULLUP);
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

  // Configura sincronização NTP para timestamp
  Serial.println("🕐 Configurando sincronização de tempo...");
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  
  // Aguarda sincronização
  int ntpAttempts = 0;
  while (!time(nullptr) && ntpAttempts < 10) {
    Serial.print(".");
    delay(1000);
    ntpAttempts++;
  }
  
  if (ntpAttempts < 10) {
    Serial.println("\n✅ Sincronização NTP bem-sucedida!");
    printDateTime();
  } else {
    Serial.println("\n⚠️ Falha na sincronização NTP. Usando horário padrão.");
  }

  // Inicializa o display OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("Erro ao iniciar o display");
    while (true); // trava o sistema se falhar
  }

  // Mensagem de boas-vindas no display
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(2);
  display.setCursor(10, 10);
  display.println("FARM TECH");
  display.setCursor(11, 40);
  display.println("SOLUTIONS");
  display.display();
  delay(2000);
}

// --- Loop principal ---
void loop() {
  // --- Leitura dos sensores P e K (simulados por botões) ---
  int buttonPState = digitalRead(BUTTON1);
  int buttonKState = digitalRead(BUTTON2);
  bool fosforo_detectado = (buttonPState == LOW);
  bool potassio_detectado = (buttonKState == LOW);

  delay(2000); // Espera entre leituras (recomendado para DHT22)

  float h = dht.readHumidity();        // Leitura da umidade
  float t = dht.readTemperature();     // Leitura da temperatura

  ldrValue = analogRead(ldrPin);       // Leitura do LDR (simulando pH)
  int phValue = ldrValue / 290;        // Conversão do valor lido para escala de pH

  // --- Exibição dos dados no Serial Monitor ---
  Serial.print("Umidade: ");
  Serial.print(h);
  Serial.print("%  Temperatura: ");
  Serial.print(t);
  Serial.println("°C");

  Serial.print("Valor do PH: ");
  Serial.println(phValue);
  Serial.print("Fosforo: ");
  Serial.print(fosforo_detectado ? "true" : "false");
  Serial.print("  Potassio: ");
  Serial.println(potassio_detectado ? "true" : "false");

  // --- Lógica para controle do relé (irrigação) ---
  bool mostrarIrrigacao = (h < 40.0); // Define se irrigação deve acontecer
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
      Serial.println("Umidade acima de 40%, bomba desligada.");
      digitalWrite(MODULORELEPIN, LOW);
      bombaLigada = false;
      break;
    case 1:
      Serial.println("Umidade abaixo de 40%, bomba ligada.");
      digitalWrite(MODULORELEPIN, HIGH);
      bombaLigada = true;
      break;
    case 2:
      Serial.println("ALERTA: Botão de chuva pressionado. Bomba desligada.");
      digitalWrite(MODULORELEPIN, LOW);
      bombaLigada = false;
      break;
    default:
      digitalWrite(MODULORELEPIN, LOW); // Segurança: mantém desligado
      bombaLigada = false;
      break;
  }

  // --- Obtém timestamp da leitura ---
  String currentTimestamp = getFormattedDateTime();
  
  // --- Exibe timestamp no Serial ---
  Serial.print("🕐 Timestamp da leitura: ");
  Serial.println(currentTimestamp);

  // --- Monta string para envio ao servidor Flask/Python ---
  String sensorData = "timestamp=" + urlEncode(currentTimestamp) + "&umidade=" + String(h) + "&temperatura=" + String(t) +
                      "&ph=" + String(phValue) + "&fosforo=" + String(fosforo_detectado ? "true" : "false") +
                      "&potassio=" + String(potassio_detectado ? "true" : "false") + "&rele=" + String(bombaLigada ? "true" : "false");

  // --- Lista de servidores para envio dos dados ---
  String servers[] = {
    "http://192.168.0.12:8000/data",
    "http://192.168.2.126:8000/data"
  };
  int numServers = sizeof(servers) / sizeof(servers[0]);

  // --- Envio dos dados para todos os servidores ---
  for (int i = 0; i < numServers; i++) {
    String serverAddress = servers[i] + "?" + sensorData;
    
    Serial.print("Enviando para servidor ");
    Serial.print(i + 1);
    Serial.print(": ");
    Serial.println(servers[i]);

    WiFiClient client;
    HTTPClient http;
    http.begin(client, serverAddress);
    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
      Serial.print("✅ Servidor ");
      Serial.print(i + 1);
      Serial.print(" - HTTP Response code: ");
      Serial.println(httpResponseCode);
      String response = http.getString();
      Serial.print("Response: ");
      Serial.println(response);
    } else {
      Serial.print("❌ Erro no servidor ");
      Serial.print(i + 1);
      Serial.print(" - ");
      Serial.println(http.errorToString(httpResponseCode));
    }
    http.end();
    
    // Pequena pausa entre requisições
    delay(100);
  }

  // --- Exibição no Display OLED ---
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);

  display.setCursor(0, 0);
  display.print("Temp: ");
  display.print(t);
  display.print(" C");

  display.setCursor(0, 20);
  display.print("Umid: ");
  display.print(h);
  display.print(" %");

  display.setCursor(0, 38);
  display.print("pH: ");
  display.print(phValue);

  display.setCursor(50, 38);
  display.print("Bomba:");
  display.print(bombaLigada ? "T" : "F");

  display.setCursor(0, 48);
  display.print("P:");
  display.print(potassio_detectado ? "T" : "F");
  display.print(" F:");
  display.print(fosforo_detectado ? "T" : "F");

  // Mostra horário da última leitura (apenas hora:minuto)
  display.setCursor(0, 56);
  display.setTextSize(1);
  String timeOnly = currentTimestamp.substring(11, 16); // Extrai apenas HH:MM
  display.print("Hora: ");
  display.print(timeOnly);

  display.display(); // Atualiza o display
}



