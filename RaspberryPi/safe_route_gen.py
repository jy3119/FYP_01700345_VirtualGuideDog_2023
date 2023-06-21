import serial
import numpy as np
import matplotlib.pyplot as plt

# Connect to the Arduino
ser = serial.Serial('/dev/ttyACM0', 9600)

# Initialize an empty occupancy grid
grid_size = 100
occupancy_grid = np.zeros((grid_size, grid_size))

# Initialize a repulsive potential field
repulsive_field = np.zeros((grid_size, grid_size))

# Repulsive coefficients (obstacles and falls)
eta_obstacle = 500.0
eta_fall = 1000.0

# Distance correction for inclined sensors
cos45 = np.cos(np.radians(45))

# Function to update the occupancy grid based on sensor readings
def update_occupancy_grid(angle, top_dist, mid_dist, bot_dist, sudden_change):
    # Update the grid based on each sensor reading
    for dist, offset in zip([top_dist, mid_dist, bot_dist], [-1, 0, 1]):
        # Correct the distance for the top and bottom sensors
        if offset != 0:
            dist *= cos45

        # Calculate the grid coordinates of the detected obstacle
        x = grid_size // 2 + int(dist * np.sin(angle))
        y = grid_size // 2 + int(dist * np.cos(angle)) + offset

        # Update the occupancy grid
        if 0 <= x < grid_size and 0 <= y < grid_size:
            occupancy_grid[x, y] = 2 if sudden_change else 1

while True:
    # Read a line from the Arduino
    line = ser.readline().decode().strip()

    # Parse the data
    angle, top_dist, mid_dist, bot_dist, sudden_change = map(int, line.split(','))

    # Convert angle to radians and adjust it to be in the range [-pi/2, pi/2]
    angle_rad = np.radians(angle - 90)

    # Update occupancy grid based on sensor readings
    update_occupancy_grid(angle_rad, top_dist, mid_dist, bot_dist, sudden_change)

    # Calculate the potential field
    for x in range(grid_size):
        for y in range(grid_size):
            pos = np.array([x, y])

            # Repulsive potential (from the obstacles)
            U_rep = 0
            if occupancy_grid[x, y] != 0:
                eta = eta_fall if occupancy_grid[x, y] == 2 else eta_obstacle
                U_rep = 0.5 * eta / occupancy_grid[x, y]

            # Total potential
            repulsive_field[x, y] = U_rep

    # Calculate the direction of the safest path (gradient of the potential field)
    grad_field = np.gradient(repulsive_field)
    safe_direction = np.arctan2(grad_field[1][grid_size // 2, grid_size - 1], grad_field[0][grid_size // 2, grid_size - 1])

    # Convert the direction to degrees and adjust it to be in the range [-90, 90]
    safe_direction_deg = np.degrees(safe_direction) + 90

    print("Safe direction (in degrees): ", safe_direction_deg)

    # Display the occupancy grid
    plt.imshow(occupancy_grid)
    plt.pause(0.01)  # Pause to allow the plot to update

ser.close()
