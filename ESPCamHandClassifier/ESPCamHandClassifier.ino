#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include "secrets.h"

WiFiClientSecure espClient;
PubSubClient client(espClient);

// ----------------------------
// WiFi connect
// ----------------------------
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

// ----------------------------
// MQTT reconnect
// ----------------------------
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");

    String clientId = "ESP32-EYE-";
    clientId += String(random(0xffff), HEX);

    if (client.connect(clientId.c_str(), mqtt_user, mqtt_pass)) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5 seconds");
      delay(5000);
    }
  }
}

// ----------------------------
// Setup
// ----------------------------
void setup() {
  Serial.begin(115200);

  setup_wifi();
  espClient.setInsecure();
  client.setServer(mqtt_server, 8883);
}

// ----------------------------
// Main loop
// ----------------------------
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  Serial.println("Publishing WALK");
  client.publish(mqtt_topic, "WALK");
  delay(10000);

  Serial.println("Publishing STOP");
  client.publish(mqtt_topic, "STOP");
  delay(10000);
}