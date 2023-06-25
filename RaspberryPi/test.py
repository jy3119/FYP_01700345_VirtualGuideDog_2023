import serial
import numpy as np
from bluepy.btle import Peripheral, UUID, DefaultDelegate
import time
import math

# Serial communication
ser = serial.Serial('/dev/ttyACM0', 9600)  # change to your Arduino's port

# Bluetooth
ble_uuid = UUID('19B10001-E8F2-537E-4F6C-D104768A1214') # Characteristic UUID
ble_service_uuid = UUID('19B10000-E8F2-537E-4F6C-D104768A1214') # Service UUID

MAX_DISTANCE = 300

# Repulsive potential field parameters
K_rep = 1.0
d_rep = 20.0


class NotificationDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        angle = int.from_bytes(data, byteorder='little')
        print('Received angle:', angle)


def potential_field(grid):
    U_rep = np.zeros(grid.shape)
    min_val = np.inf
    min_idx = None

    for i in range(grid.shape[1]):
        for j in range(grid.shape[0]):
            if grid[j, i] == 1:  # obstacle
                U_rep[j, i] = 0.5 * K_rep * ((1.0/d_rep) ** 2)
            else:  # free space
                U_rep[j, i] = 0

            if U_rep[j, i] < min_val:
                min_val = U_rep[j, i]
                min_idx = (j, i)

    return min_idx


# Process sensor data
def process_data(data):
    grid_size = (360, 180)
    grid = np.zeros(grid_size)
    data = data.decode().strip() 
    data = data.split(',')
    angle = int(data[0])
    dist_top = int(data[1]) * math.cos(math.radians(45))
    dist_middle = int(data[2])
    dist_bottom = int(data[3]) * math.cos(math.radians(45))
    sudden_change_downward = int(data[4])

    # Update occupancy grid
    
    if dist_top < MAX_DISTANCE:
        grid[angle, min(int(dist_top), grid_size[1] - 1)] = 1
    if dist_middle < MAX_DISTANCE:
        grid[angle, min(int(dist_middle), grid_size[1] - 1)] = 1
    if dist_bottom < MAX_DISTANCE:
        grid[angle, min(int(dist_bottom), grid_size[1] - 1)] = 1
    if sudden_change_downward == 1:
        grid[angle, :] = 3  # indicate a fall

    # Calculate safest direction
    min_idx = potential_field(grid)
    return min_idx[0] - 90  # subtract 90 to shift from [0, 180] to [-90, 90]

# Main loop
while True:
    data = ser.readline().strip()
    angle = process_data(data)
    
    try:
        # Connect to the Arduino Nano 33 BLE
        # peripheral = Peripheral()
        peripheral = Peripheral('A1:DC:B9:DC:2E:BA')
        peripheral.connect('A1:DC:B9:DC:2E:BA')

        # Discover the service and characteristic
        service = peripheral.getServiceByUUID(ble_service_uuid)
        characteristic = service.getCharacteristics(ble_uuid)[0]

        # Enable notifications
        delegate = NotificationDelegate()
        peripheral.setDelegate(delegate)
        peripheral.writeCharacteristic(characteristic.valHandle + 1, b"\x01\x00", True)

        # Send the angle as a notification
        characteristic.write(bytes([angle]))

        # Wait for notifications
        while peripheral.waitForNotifications(1):
            pass

        # Disconnect from the Arduino Nano 33 BLE
        peripheral.disconnect()
    except Exception as e:
        print('Error:', str(e))

    time.sleep(0.01)

