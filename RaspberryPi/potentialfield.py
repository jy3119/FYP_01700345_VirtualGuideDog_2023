import serial
import matplotlib.pyplot as plt
import numpy as np
import math

# Open serial port
ser = serial.Serial('COM5', 9600, timeout=1)
ser.flush()

# Create a grid
grid = np.zeros((200, 200))

def calculate_potential_field(grid):
    # Initialize the potential field
    potential_field = np.zeros(grid.shape)

    # Compute attractive field
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            potential_field[i, j] = np.sqrt((i - 100)**2 + (j - 200)**2) + 0.001 * (200 - j)

    # Modify potential field to account for obstacles
    potential_field += grid * float('inf')

    return potential_field

def find_safest_direction(potential_field):
    # Search for the minimal potential direction
    min_direction = 0  # default direction if no lower potential found
    min_potential = float('inf')
    for angle in np.arange(-180, 180, 1):
        angle_rad = np.radians(angle)
        x = 100 + int(100 * np.cos(angle_rad))
        y = 100 + int(100 * np.sin(angle_rad))
        if x >= 0 and x < 200 and y >= 0 and y < 200:
            if potential_field[y, x] < min_potential:
                min_potential = potential_field[y, x]
                min_direction = angle

    return min_direction

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
                    if x >= 0 and x < 200 and y >= 0 and y < 200:
                        grid[int(y), int(x)] = 1
           
            if downward == 1:
                for y in range(200):
                    x = int(100 + 100 * math.cos(angle_rad))
                    if x >= 0 and x < 200:
                        grid[y, x] = 1

    except Exception as e:
        print(e)

    # Calculate potential field
    potential_field = calculate_potential_field(grid)
    safest_direction = find_safest_direction(potential_field)

    # Add the safest direction line to the grid for visualization
    if safest_direction is not None:
        safest_direction_rad = np.radians(safest_direction)
        for r in range(100):
            x = 100 + int(r * np.cos(safest_direction_rad))
            y = 100 + int(r * np.sin(safest_direction_rad))
            if x >= 0 and x < 200 and y >= 0 and y < 200:
                grid[y, x] = 2

    # Visualize the grid
    plt.imshow(grid, cmap='Greys', origin='lower')
    plt.title(f'Safest direction: {safest_direction} degrees')
    plt.pause(0.01)

