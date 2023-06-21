#include <Arduino_LSM9DS1.h>
#include <Arduino_MadgwickIMU.h>
#include <ArduinoBLE.h>

// BLE service and characteristic
BLEService safeDirectionService("180D");
BLEIntCharacteristic safeDirectionChar("2A37", BLERead | BLEWrite);

// Vibration motors connected to pins 2-6
int motors[5] = {2, 3, 4, 5, 6};

// Angle thresholds for the motors
int thresholds[5] = {0, 45, 90, 135, 180};

// Current safe direction
int safeDirection = 0;

// Update frequency for the Madgwick filter
float updateFreq = 36.0;

// Create Madgwick filter
Madgwick filter;
float roll, pitch, yaw;

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

  // Initialize the Madgwick filter
  filter.begin(updateFreq);

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
      filter.updateIMU(gx, gy, gz, ax, ay, az);
      roll = filter.getRoll();
      pitch = filter.getPitch();
      yaw = filter.getYaw();

      // Since yaw ranges from -180 to 180, convert it to 0 to 180
      if (yaw < 0) yaw = 180 + yaw;

      // Initialize all motors to off
      for (int i = 0; i < 5; i++) {
        digitalWrite(motors[i], LOW);
      }

      // Update safe direction if there's new data
      if (safeDirectionChar.written()) {
        safeDirection = safeDirectionChar.value();
      }

      // Calculate the difference between the safe direction and the current head direction
      int angleDiff = safeDirection - yaw;

      // Turn on the appropriate motor based on the angle difference
      for (int i = 0; i < 5; i++) {
        if (angleDiff <= thresholds[i]) {
          digitalWrite(motors[i], HIGH);
          break;
        }
      }
    }

    delay(1000 / updateFreq);
  }
}
