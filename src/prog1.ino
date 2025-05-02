// Definição das Bibliotecas: Sensores, Display
#include <Adafruit_Sensor.h>
#include <DHT.h>                                                            // Bibioteca do sensor de temperatura e umidade
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>                                               // Biblioteca para o display do tipo Oled

// Definição da Biblioteca WiFi
#include <WiFi.h>
#include <HTTPClient.h>                                                     // Requisição HTTP GET para um endereço IP e porta específico

// Variáveis para as credenciais de rede - simulação
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// Definição dos pinos utilizados no Esp32 para leitura DHT22
#define BUTTON1 2
#define BUTTON2 18
#define MODULORELEPIN 4                                                     // Módulo relê para acionamento da bomba de água - simulado pelo led vermelho
#define DHTPIN 5                                                            // Pino digital do Esp32 conectado ao DHT22 - sensor de temp. e umid.
#define DHTTYPE DHT22                                                       // Tipo de sensor DHT (DHT22)

// Definição Oled
#define SCREEN_WIDTH 128                                                    // Largura do display OLED, em pixels
#define SCREEN_HEIGHT 64                                                    // Altura do display OLED, em pixels
#define OLED_RESET -1                                                       // Pino de reset (deixe como -1 se não estiver conectado)

// Inicializa o sensor DHT
DHT dht(DHTPIN, DHTTYPE); 

// Pino analogico do Esp32 conectado ao LDR
const int ldrPin = 34; 
int ldrValue = 0;

// Referente ao menu do Oled
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Configuração das portas do ESP32, monitor serial, sensor DHT e outros
void setup() {
  Serial.begin(115200);
  Serial.println("");
  Serial.println("Sensor de PH            Inicializando...");
  Serial.println("Sensor de Temperatura   Inicializando...");
  Serial.println("Sensor de Umidade       Inicializando...");
  Serial.println("Sensor de Potássio      Inicializando...");
  Serial.println("Sensor de Fósforo       Inicializando...");
  Serial.println("Display Digital         Inicializando...");
  Serial.println("");
  Serial.println("Conectando-se ao Wi-Fi...");
  pinMode(BUTTON1, INPUT_PULLUP);                                           // Define pino 2 como entrada para o botão 1 e configurada com resistor de entrada na porta com sinal GND
  pinMode(BUTTON2, INPUT_PULLUP);                                           // Define pino 18 como entrada para o botão 2 e configurada com resistor de entrada na porta com sinal GND
  pinMode(MODULORELEPIN, OUTPUT);                                           // Define pino 4 como saida para controle do módulo relê
  dht.begin();
  
  // Conexão com a rede Wi-Fi
  WiFi.begin(ssid, password, 6);                                            // Especificando o canal 6

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print("************************");
  }
  Serial.println("");
  Serial.println("Wi-Fi conectado!");
  Serial.print("Endereço IP: ");
  Serial.println(WiFi.localIP());
  Serial.print("");
  Serial.println("************************");

  // Conexão display Oled
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {                           // Endereço 0x3C para displays comuns
    Serial.println(F("Falha ao iniciar o Display"));
    for(;;);                                                                 // Loop infinito se a inicialização falhar
  }

  // Limpa o buffer do display
  display.clearDisplay();

  // Define a cor do texto para branco
  display.setTextColor(SSD1306_WHITE);
 
  // Define o tamanho do texto
  display.setTextSize(2);

  // Define a posição do cursor
  display.setCursor(10, 10);
  display.println("FARM TECH");
  display.setCursor(11, 40);
  display.println("SOLUTIONS");
  display.display();                                                         // Exibe o buffer
  delay(2000);                                                               // Mostra a mensagem por 5 segundos
}

void loop() {
  
  // Controle do botão (P e K)
  int buttonPState = digitalRead(BUTTON1);
  int buttonKState = digitalRead(BUTTON2);
  String fosforo = (buttonPState == LOW) ? "presente" : "ausente";          // Operador ternário -> condição ? valor_se_verdadeiro : valor_se_falso;
  String potassio = (buttonKState == LOW) ? "presente" : "ausente";
  String f = fosforo;
  String p = potassio;

  // Delay recomendado entre leituras para DHT22 é de pelo menos 2 segundos.
  delay(2000);
  float h = dht.readHumidity();                                             // Lê a umidade e salva na variável h.
  float t = dht.readTemperature();                                          // Lê a temperatura em Celsius e salva na variável t.
  
  // Leitura do sensor LDR e salvo na variável 
  ldrValue = analogRead(ldrPin);

  // Valores exibidos no monitor serial
  Serial.print(F("Umidade: "));
  Serial.print(h);
  Serial.print(F("%  Temperatura: "));
  Serial.print(t);
  Serial.println(F("°C "));
  Serial.print("Valor do PH: ");
  Serial.println(ldrValue/290);
  Serial.print(F("Fosforo: "));
  Serial.print(f);
  Serial.print(F("  Potassio: "));
  Serial.println(p);
  
  // Leitura do sensor LDR (pH simulado)
  ldrValue = analogRead(ldrPin);
  int phValue = ldrValue / 290;                                             // Declaração e cálculo de phValue aproximado

  // Lógica de controle do relé (ACIONA LED VERMELHO) baseada na umidade.
  bool mostrarIrrigacao = (h < 40.0);
  digitalWrite(MODULORELEPIN, mostrarIrrigacao ? HIGH : LOW);
  String releStatus = mostrarIrrigacao ? "on" : "off";

  // Formatar os dados para envio via HTTP GET
  String sensorData = "umidade=" + String(h) + "&temperatura=" + String(t) +
                      "&ph=" + String(phValue) + "&fosforo=" + fosforo +
                      "&potassio=" + potassio + "&rele=" + releStatus;

  // Endereço do servidor Python 
  String serverAddress = "http://192.168.0.11:8000/data?" + sensorData;

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
    Serial.println("Error on HTTP request: ");
    Serial.println(http.errorToString(httpResponseCode));
  }

  http.end();

  // *** Exibição no OLED ***
  display.clearDisplay();
  display.setTextSize(1,1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.print("Temp: ");
  display.print(t);                                                         // Exibe o valor da temperatura
  display.print(" C");
  display.setCursor(0, 20);
  display.print("Umid: ");
  display.print(h);                                                         // Exibe o valor da umidade
  display.print(" %");
  display.setCursor(0, 40);
  display.print("ph: ");
  display.println(ldrValue/290);                                            // Exibe o valor do LDR convertido lux -> valores de ph de 0 até 14
  display.setCursor(0, 55);
  display.print("P:");
  display.print(p);
  display.print(" F:");
  display.print(f);                                            
  display.display();
 }

   