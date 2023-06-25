#include <Arduino_LSM9DS1.h>
#include <MadgwickAHRS.h>
#include <ArduinoBLE.h>

// BLE service and characteristic
BLEService safeDirectionService("180D");
BLEIntCharacteristic safeDirectionChar("2A37", BLERead | BLEWrite);

// Vibration motors connected to pins 2-6
int motors[5] = {2, 3, 4, 5, 6};

// Update frequency for the Madgwick filter
float updateFreq = 36.0;

// Create Madgwick filter
Madgwick filter;

void setup() {
  Serial.begin(9600);

  // Initialize IMU
  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  // Initialize motor pins as outputs
  for (int i = 0; i < 5; i++) {
    pinMode(motors[i], OUTPUT);
  }

  // Begin BLE
  if (!BLE.begin()) {
    Serial.println("Failed to start BLE!");
    while (1);
  }

  // Set the local name and service
  BLE.setLocalName("Safe Direction Peripheral");
  BLE.setAdvertisedService(safeDirectionService);

  // Add the characteristic
  safeDirectionService.addCharacteristic(safeDirectionChar);

  // Add the service
  BLE.addService(safeDirectionService);

  // Start advertising
  BLE.advertise();
}

void loop() {
  // Check for a central device to connect
  BLEDevice central = BLE.central();

  // If a central device is connected, read the IMU and update the motors
  if (central) {
    // Read IMU
    if (IMU.accelerationAvailable() && IMU.gyroscopeAvailable()) {
      float ax, ay, az, gx, gy, gz;
      IMU.readAcceleration(ax, ay, az);
      IMU.readGyroscope(gx, gy, gz);

      // Update the Madgwick filter
      filter.update(gx, gy, gz, ax, ay, az);
      float roll, pitch, yaw;
      filter.getEulerAngles(roll, pitch, yaw);

      // Initialize all motors to off
      for (int i = 0; i < 5; i++) {
        digitalWrite(motors[i], LOW);
      }

      // Update safe direction if there's new data
      if (safeDirectionChar.written()) {
        int safeDirection = safeDirectionChar.value();

        // Calculate the difference between the safe direction and the current head direction
        int angleDiff = safeDirection - yaw;

        // Only provide haptic feedback if the safe direction is in front
        if (angleDiff >= -90 && angleDiff <= 90) {
          // Turn on the appropriate motor based on the angle difference
          if (angleDiff >= -90 && angleDiff < -54) {
            digitalWrite(motors[0], HIGH); // far left
          }
          else if (angleDiff >= -54 && angleDiff < -18) {
            digitalWrite(motors[1], HIGH); // left
          }
          else if (angleDiff >= -18 && angleDiff < 18) {
            digitalWrite(motors[2], HIGH); // center
          }
          else if (angleDiff >= 18 && angleDiff < 54) {
            digitalWrite(motors[3], HIGH); // right
          }
          else if (angleDiff >= 54 && angleDiff <= 90) {
            digitalWrite(motors[4], HIGH); // far right
          }
        }
      }
    }

    delay(1000 / updateFreq);
  }
}


