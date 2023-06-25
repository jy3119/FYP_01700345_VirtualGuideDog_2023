import serial
import numpy as np
from bleno import *
import time
import math

# Serial communication
ser = serial.Serial('/dev/ttyACM0', 9600)  # change to your Arduino's port
bleno = Bleno()

# Occupancy grid size
grid_size = (360, 180)

# Repulsive potential field parameters
K_rep = 1.0
d_rep = 20.0

# Setup Bluetooth
class AngleCharacteristic(Characteristic):
    def __init__(self):
        Characteristic.__init__(self, {
            'uuid': 'fc0a',
            'properties': ['write'],
            'value': None
        })
        self._value = 0
        self._updateValueCallback = None

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        self._value = data
        print('Write request: value =', self._value)
        callback(Characteristic.RESULT_SUCCESS)

def onStateChange(state):
    print('on -> stateChange: ' + state)
    if (state == 'poweredOn'):
        bleno.startAdvertising('raspberrypi', ['fc0a'])
    elif (state == 'poweredOff'):
        bleno.stopAdvertising()

bleno.on('stateChange', onStateChange)

angle_char = AngleCharacteristic()
bleno.on('advertisingStart', lambda err: bleno.setServices([bleno.PrimaryService({
    'uuid': 'fc0a',
    'characteristics': [
        angle_char
    ]
})]))

bleno.start()

# Potential field algorithm
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
    grid = np.zeros(grid_size)
    data = data.split(',')
    angle = int(data[0])
    dist_top = int(data[1]) * math.cos(math.radians(45))
    dist_middle = int(data[2])
    dist_bottom = int(data[3]) * math.cos(math.radians(45))
    sudden_change_downward = int(data[4])

    # Update occupancy grid
    if dist_top < MAX_DISTANCE:
        grid[angle, min(dist_top, grid_size[1] - 1)] = 1
    if dist_middle < MAX_DISTANCE:
        grid[angle, min(dist_middle, grid_size[1] - 1)] = 1
    if dist_bottom < MAX_DISTANCE:
        grid[angle, min(dist_bottom, grid_size[1] - 1)] = 1
    if sudden_change_downward == 1:
        grid[angle, :] = 3  # indicate a fall

    # Calculate safest direction
    min_idx = potential_field(grid)
    return min_idx[0] - 90  # subtract 90 to shift from [0, 180] to [-90, 90]

# Main loop
while True:
    data = ser.readline().strip()
    angle = process_data(data)
    angle_char._updateValueCallback = str(angle).encode()
    time.sleep(0.01)

