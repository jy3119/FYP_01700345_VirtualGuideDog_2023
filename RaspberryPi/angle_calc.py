import serial
import time

# Connect to the Arduino
ser = serial.Serial('/dev/ttyACM0', 9600)
time.sleep(2) # wait for the serial connection to initialize

def calculate_angle():
    min_obstacle_angle = None
    min_obstacle_value = float('inf')

    while True:
        if ser.in_waiting:
            # Read a line from the serial port
            line = ser.readline().decode('utf-8').strip()
            # Parse the data
            data = line.split(',')
            angle = int(data[0])
            top = int(data[1]) if data[1] != '-1' else float('inf')
            middle = int(data[2]) if data[2] != '-1' else float('inf')
            bottom = int(data[3]) if data[3] != '-1' else float('inf')

            # Find the maximum obstacle value for this angle
            max_obstacle_value = max(top, middle, bottom)

            # If this angle has less obstacles, update our min_obstacle variables
            if max_obstacle_value < min_obstacle_value:
                min_obstacle_value = max_obstacle_value
                min_obstacle_angle = angle

        # If we have finished a scan (back at 0 degrees), break the loop
        if angle == 0 and min_obstacle_angle is not None:
            break

    return (min_obstacle_angle*-1)  + 90

# Run the function to get the angle with the least obstacles
angle = calculate_angle()
print(f"The angle with the least obstacles is: {angle}")
