def main():
    ser = serial.Serial('/dev/ttyACM0', 9600)
    data = {}
    while True:
        line = ser.readline()
        parsed_data = parse_data(line)
        if parsed_data is None:
            continue
        angle, top, middle, bottom, _ = parsed_data
        if angle not in data:
            data[angle] = []
        data[angle].append(top)
        data[angle].append(middle)
        data[angle].append(bottom)

        # Process the data once we have collected from all angles
        if len(data) == 19:  # 19 distinct angles from 0 to 180 in steps of 10
            best_angle = find_best_angle(data)
            print("Best angle: ", best_angle)
            data = {}  # reset the data
