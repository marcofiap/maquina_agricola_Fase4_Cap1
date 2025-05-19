// --- Bibliotecas para sensores e display OLED ---
#include <Adafruit_Sensor.h>
#include <DHT.h>                        // Biblioteca para sensor de temperatura e umidade DHT22
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>          // Biblioteca para display OLED

// --- Bibliotecas de comunicação Wi-Fi e HTTP ---
#include <WiFi.h>
#include <HTTPClient.h>                // Para enviar dados via HTTP GET

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
  String fosforo = (buttonPState == LOW) ? "presente" : "ausente";
  String potassio = (buttonKState == LOW) ? "presente" : "ausente";

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
  Serial.print(fosforo);
  Serial.print("  Potassio: ");
  Serial.println(potassio);

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

  String releStatus = bombaLigada ? "on" : "off";

  // --- Monta string para envio ao servidor Flask/Python ---
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
  display.print(releStatus);

  display.setCursor(0, 56);
  display.print("P:");
  display.print(potassio);
  display.print(" F:");
  display.print(fosforo);

  display.display(); // Atualiza o display
}



