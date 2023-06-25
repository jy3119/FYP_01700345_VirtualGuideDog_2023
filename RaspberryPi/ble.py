from bluepy import btle

# Define the UUIDs for the BLE service and characteristic
service_uuid = "19B10000-E8F2-537E-4F6C-D104768A1214"
char_uuid = "19B10001-E8F2-537E-4F6C-D104768A1214"

# Scan for BLE devices
scanner = btle.Scanner()
devices = scanner.scan(5)  # Scan for 5 seconds
arduino_device = None

for dev in devices:
    if dev.addr == 'A1:DC:B9:DC:2E:BA':
        arduino_device = dev
        break

if arduino_device is None:
    print("Arduino Nano 33 BLE not found.")
    exit()

# Connect to the Arduino Nano 33 BLE
peripheral = btle.Peripheral(arduino_device)
service = peripheral.getServiceByUUID(service_uuid)
char = service.getCharacteristics(char_uuid)[0]

# Read the current value of the characteristic
value = char.read()
print("Current value:", value[0])

# Write a new value to the characteristic
new_value = 1
char.write(bytes([new_value]), True)

# Disconnect from the Arduino Nano 33 BLE
peripheral.disconnect()
