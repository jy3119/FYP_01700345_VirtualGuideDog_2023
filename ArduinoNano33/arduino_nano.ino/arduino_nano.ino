#include <ArduinoBLE.h>

#define VIBRATOR_1_PIN 2
#define VIBRATOR_2_PIN 3
#define VIBRATOR_3_PIN 4
#define VIBRATOR_4_PIN 5
#define VIBRATOR_5_PIN 6

void setup() {
  Serial.begin(9600);
  while(!Serial);

  pinMode(VIBRATOR_1_PIN, OUTPUT);
  pinMode(VIBRATOR_2_PIN, OUTPUT);
  pinMode(VIBRATOR_3_PIN, OUTPUT);
  pinMode(VIBRATOR_4_PIN, OUTPUT);
  pinMode(VIBRATOR_5_PIN, OUTPUT);

  if (!BLE.begin()) {
    Serial.println("starting BLE failed!");
    while (1);
  }

  Serial.println("BLE started");
}

void loop() {
  BLEDevice peripheral = BLE.central();

  if (peripheral) {
    Serial.print("Connected to Central: ");
    Serial.println(peripheral.address());

    if (peripheral.discoverAttributes()) {
      Serial.println("Attributes discovered");
    } else {
      Serial.println("Attribute discovery failed!");
      peripheral.disconnect();
      return;
    }

    BLEService service = peripheral.service("fc0a");

    if (!service) {
      Serial.println("Service not found!");
      peripheral.disconnect();
      return;
    }

    BLECharacteristic characteristic = service.characteristic("fc0a");

    if (!characteristic) {
      Serial.println("Characteristic not found!");
      peripheral.disconnect();
      return;
    }

    if (characteristic.canRead()) {
      characteristic.readValue();
      int angle = characteristic.value().toInt();

      // clear all motors
      digitalWrite(VIBRATOR_1_PIN, LOW);
      digitalWrite(VIBRATOR_2_PIN, LOW);
      digitalWrite(VIBRATOR_3_PIN, LOW);
      digitalWrite(VIBRATOR_4_PIN, LOW);
      digitalWrite(VIBRATOR_5_PIN, LOW);

      if (angle >= -90 && angle < -54) {
        digitalWrite(VIBRATOR_1_PIN, HIGH);
      } else if (angle >= -54 && angle < -18) {
        digitalWrite(VIBRATOR_2_PIN, HIGH);
      } else if (angle >= -18 && angle <= 18) {
        digitalWrite(VIBRATOR_3_PIN, HIGH);
      } else if (angle > 18 && angle <= 54) {
        digitalWrite(VIBRATOR_4_PIN, HIGH);
      } else if (angle > 54 && angle <= 90) {
        digitalWrite(VIBRATOR_5_PIN, HIGH);
      }
    }
  }
}
