import numpy as np
import math
from bluepy.btle import Peripheral, UUID


def receive_data():
    data = SerialData() # dummy placeholder for real data
    return data

def build_occupancy_grid(data):
    occupancy_grid = np.zeros((10, 10))  # replace with actual grid size
    for d in data:
        occupancy_grid[d.y][d.x] = d.state
    return occupancy_grid

def compute_potential_field(occupancy_grid, goal=[9, 9]): # top right corner as goal
    grid_size = occupancy_grid.shape
    potential_field = np.zeros(grid_size)

    # Apply attractive potential from goal
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            potential_field[i][j] += np.linalg.norm(np.array([i,j])-np.array(goal))

    # Apply repulsive potential from obstacles
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            if occupancy_grid[i][j] == 1:  # obstacle
                potential_field[i][j] += 100
            elif occupancy_grid[i][j] == 3:  # falls
                potential_field[i][j] += 200

    return potential_field

def compute_gradient(potential_field, current_position):
    dx = np.gradient(potential_field, axis=1)[current_position[1]][current_position[0]]
    dy = np.gradient(potential_field, axis=0)[current_position[1]][current_position[0]]
    return dx, dy

def get_angle(dx, dy):
    # Your coordinate system has the y-axis as -90 and the x-axis as 90.
    # The diagonal from origin to the top right corner represents 0 degrees.
    angle = math.atan2(dy, dx)
    angle = math.degrees(angle)
    return angle

def get_safest_direction(potential_field, current_position=[0, 0]):
    dx, dy = compute_gradient(potential_field, current_position)
    return get_angle(dx, dy)

def main():
    p = Peripheral('your_BLE_device', 'public')  # connect to BLE device
    svc = p.getServiceByUUID('your_BLE_service')  # replace with your service UUID
    ch = svc.getCharacteristics('your_BLE_characteristic')[0]  # replace with your characteristic UUID

    while True:
        data = receive_data()
        occupancy_grid = build_occupancy_grid(data)
        potential_field = compute_potential_field(occupancy_grid)
        safest_direction = get_safest_direction(potential_field)
        print(f"Safest direction to walk in: {safest_direction} degrees")

        # write the safest direction to the BLE device
        ch.write(bytes(str(safest_direction), 'utf-8'))

        time.sleep(1)  # delay before next update
