#include <Arduino_LSM9DS1.h>
#include <MadgwickAHRS.h>
#include <ArduinoBLE.h>

BLEService safeDirectionService("180D");
BLEIntCharacteristic safeDirectionChar("2A37", BLERead | BLEWrite);

const int motors[5] = {2, 3, 4, 5, 6};
const float updateFreq = 36.0;

Madgwick filter;

void setup() {
  Serial.begin(9600);

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  for (int i = 0; i < 5; i++) {
    pinMode(motors[i], OUTPUT);
  }

  if (!BLE.begin()) {
    Serial.println("Failed to start BLE!");
    while (1);
  }

  BLE.setLocalName("Safe Direction Peripheral");
  BLE.setAdvertisedService(safeDirectionService);

  safeDirectionService.addCharacteristic(safeDirectionChar);

  BLE.addService(safeDirectionService);

  BLE.advertise();
}

void loop() {
  BLEDevice central = BLE.central();

  if (central) {
    if (IMU.accelerationAvailable() && IMU.gyroscopeAvailable()) {
      float ax, ay, az, gx, gy, gz;
      IMU.readAcceleration(ax, ay, az);
      IMU.readGyroscope(gx, gy, gz);

      filter.updateIMU(gx, gy, gz, ax, ay, az);
      float roll = filter.getRoll();
      float pitch = filter.getPitch();
      float yaw = filter.getYaw();

      for (int i = 0; i < 5; i++) {
        digitalWrite(motors[i], LOW);
      }

      if (safeDirectionChar.written()) {
        int safeDirection = safeDirectionChar.value();
        int angleDiff = safeDirection - yaw;

        if (angleDiff >= -90 && angleDiff <= 90) {
          if (angleDiff < -54) {
            digitalWrite(motors[0], HIGH); // far left
          }
          else if (angleDiff < -18) {
            digitalWrite(motors[1], HIGH); // left
          }
          else if (angleDiff < 18) {
            digitalWrite(motors[2], HIGH); // center
          }
          else if (angleDiff < 54) {
            digitalWrite(motors[3], HIGH); // right
          }
          else {
            digitalWrite(motors[4], HIGH); // far right
          }
        }
      }
    }

    delay(1000 / updateFreq);
  }
}

