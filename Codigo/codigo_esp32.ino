#include <Wire.h>
#include "MAX30105.h"
#include "heartRate.h"
#include <WiFi.h>
#include <PubSubClient.h>

// Configuración de la red WiFi
const char* ssid = "INFINITUM4463";
const char* password = "2J9UheLPkJ";

// Configuración del broker MQTT
const char* mqtt_server = "192.168.1.70"; // IP de tu broker Mosquitto
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

// Instancia de libreria para sensor de Latidos
MAX30105 particleSensor;

const byte RATE_SIZE = 4; // Aumenta esto para más promedios. 4 es bueno.
byte rates[RATE_SIZE]; // Array de ritmos cardíacos
byte rateSpot = 0;
long lastBeat = 0; // Tiempo en el que ocurrió el último latido

float beatsPerMinute;
int beatAvg;

bool sensorEnabled = false; // Variable para habilitar/deshabilitar el sensor

void callback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.print("Mensaje recibido: ");
  Serial.println(message);

  // Comparar el mensaje y habilitar/deshabilitar el sensor
  if (message == "true") {
    sensorEnabled = true;
    Serial.println("Sensor habilitado.");
  } else if (message == "false") {
    sensorEnabled = false;
    Serial.println("Sensor deshabilitado.");
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Conectando al broker MQTT...");
    if (client.connect("ESP32Client")) {
      Serial.println("Conectado");
      // Suscribirse a temas si es necesario
      client.subscribe("control/sensor");
      client.setCallback(callback);
    } else {
      Serial.print("Falló, rc=");
      Serial.print(client.state());
      Serial.println(" Intentando de nuevo en 3 segundos...");
      delay(3000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("Initializing...");
  WiFi.begin(ssid, password);
  
  // Se conecta a internet
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Conectando a WiFi...");
  }
  Serial.println("Conectado a WiFi");

  client.setServer(mqtt_server, mqtt_port);

  // Initialize sensor
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) // Use default I2C port, 400kHz speed
  {
    Serial.println("MAX30105 was not found. Please check wiring/power. ");
    while (1);
  }
  Serial.println("Place your index finger on the sensor with steady pressure.");

  particleSensor.setup(); // Configure sensor with default settings
  particleSensor.setPulseAmplitudeRed(0x0A); // Turn Red LED to low to indicate sensor is running
  particleSensor.setPulseAmplitudeGreen(0); // Turn off Green LED
  particleSensor.enableDIETEMPRDY();
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  if (sensorEnabled) {
    long irValue = particleSensor.getIR();
    float temperature = particleSensor.readTemperature();

    Serial.print("temperature C=");
    Serial.print(temperature, 4);

    if (checkForBeat(irValue) == true) {
      // We sensed a beat!
      long delta = millis() - lastBeat;
      lastBeat = millis();

      beatsPerMinute = 60 / (delta / 1000.0);

      if (beatsPerMinute < 255 && beatsPerMinute > 20) {
        rates[rateSpot++] = (byte)beatsPerMinute; // Store this reading in the array
        rateSpot %= RATE_SIZE; // Wrap variable

        // Take average of readings
        beatAvg = 0;
        for (byte x = 0 ; x < RATE_SIZE ; x++)
          beatAvg += rates[x];
        beatAvg /= RATE_SIZE;
      }
    }

    Serial.print(", Avg BPM=");
    Serial.print(beatAvg);

    // Publicar los valores directamente 
    String payload = "Temperatura: " + String(temperature) + ", RPM: " + String(beatAvg);
    client.publish("test/topic", payload.c_str());
    
    if (irValue < 50000)
      Serial.print(" Sin dedo?");

    Serial.println();
  }
}