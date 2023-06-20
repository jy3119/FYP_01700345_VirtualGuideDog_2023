#include <NewPing.h>
#include <Servo.h>

#define TRIGGER_PIN_TOP  2  
#define ECHO_PIN_TOP     3  

#define TRIGGER_PIN_MIDDLE  4
#define ECHO_PIN_MIDDLE     5

#define TRIGGER_PIN_BOTTOM  6
#define ECHO_PIN_BOTTOM     8
#define TRIGGER_PIN_DOWNWARD  10
#define ECHO_PIN_DOWNWARD     11

#define MAX_DISTANCE 200
#define MAX_CHANGE 10  // Maximum allowed change in distance
#define NUM_READINGS 5
#define HISTORY_LENGTH 5

NewPing sonarTop(TRIGGER_PIN_TOP, ECHO_PIN_TOP, MAX_DISTANCE);
NewPing sonarMiddle(TRIGGER_PIN_MIDDLE, ECHO_PIN_MIDDLE, MAX_DISTANCE);
NewPing sonarBottom(TRIGGER_PIN_BOTTOM, ECHO_PIN_BOTTOM, MAX_DISTANCE);
NewPing sonarDownward(TRIGGER_PIN_DOWNWARD, ECHO_PIN_DOWNWARD, MAX_DISTANCE);

Servo servo;

int readingsTop[NUM_READINGS];
int readingsMiddle[NUM_READINGS];
int readingsBottom[NUM_READINGS];
int readingsDownward[HISTORY_LENGTH];
int readIndex = 0;

void setup() {
  Serial.begin(9600);
  servo.attach(9);

  for (int thisReading = 0; thisReading < NUM_READINGS; thisReading++) {
    readingsTop[thisReading] = 0;
    readingsMiddle[thisReading] = 0;
    readingsBottom[thisReading] = 0;
  }
  for (int thisReading = 0; thisReading < HISTORY_LENGTH; thisReading++) {
    readingsDownward[thisReading] = sonarDownward.ping_cm();
    delay(50);
  }
}

void loop() {
  for (int i = 0; i <= 180; i+=10) {
    servo.write(i);
    delay(100); 

    readingsTop[readIndex] = sonarTop.ping_cm();
    readingsMiddle[readIndex] = sonarMiddle.ping_cm();
    readingsBottom[readIndex] = sonarBottom.ping_cm();
    readingsDownward[readIndex] = sonarDownward.ping_cm();

    readIndex++;
  
    if (readIndex >= NUM_READINGS) {
      readIndex = 0;
    }

    int medianTop = findMedian(readingsTop, NUM_READINGS);
    int medianMiddle = findMedian(readingsMiddle, NUM_READINGS);
    int medianBottom = findMedian(readingsBottom, NUM_READINGS);

    // Check for sudden change in downward sensor
    int suddenChangeDownward = abs(readingsDownward[readIndex] - readingsDownward[(readIndex - 1 + HISTORY_LENGTH) % HISTORY_LENGTH]) > MAX_CHANGE;

    // Serial.print("Angle: ");
    Serial.print(i);
    Serial.print(",");
    Serial.print(medianTop);
    Serial.print(",");
    Serial.print(medianMiddle);
    Serial.print(",");
    Serial.print(medianBottom);
    Serial.print(",");
    Serial.println(suddenChangeDownward);
  }
}

int findMedian(int* data, int size) {
  int sortedData[size];
  memcpy(sortedData, data, size * sizeof(int));
  sort(sortedData, size);
  return sortedData[size / 2];
}

void sort(int* data, int size) {
  for (int i = 0; i < size - 1; i++) {
    for (int j = i + 1; j < size; j++) {
      if (data[j] < data[i]) {
        int temp = data[i];
        data[i] = data[j];
        data[j] = temp;
      }
    }
  }
}
