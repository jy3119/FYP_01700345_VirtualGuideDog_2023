import serial
import matplotlib.pyplot as plt
import numpy as np
import math

# Open serial port
ser = serial.Serial('COM5', 9600, timeout=1)
ser.flush()

# Create a grid
grid = np.zeros((200, 200))

# Read from the Arduino
while True:
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            data = line.split(',')
           
            # Extract the angle and sensor readings
            angle = int(data[0])
            top = int(data[1])
            middle = int(data[2])
            bottom = int(data[3])
            downward = int(data[4])
           
            # Calculate the grid indices
            angle_rad = math.radians(angle)
           
            for value in [top, middle, bottom]:
                if value != -1:
                    x = 100 + value * math.cos(angle_rad)
                    y = 100 + value * math.sin(angle_rad)
                    grid[int(y), int(x)] = 1
           
            # if downward == 1:
            #     for y in range(200):
            #         grid[y, int(100 + 100 * math.cos(angle_rad))] = 1
                   
    except Exception as e:
        print(e)

    # Visualize the grid
    plt.imshow(grid, cmap='Greys', origin='lower')
    plt.pause(0.01)