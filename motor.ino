#include <Stepper.h>

const int motorPin1 = 2;
const int motorPin2 = 15;  // GPIO 15 para ESP32
const int motorPin3 = 4;
const int motorPin4 = 16;  // GPIO 16 para ESP32
const int stepsScale = 2048;  // Los motores 28BYJ-48 generalmente tienen 2048 pasos por revolución
Stepper stepper1(stepsScale, motorPin1, motorPin3, motorPin2, motorPin4);

int noSteps = 180;

void setup() {
  Serial.begin(9600);
  stepper1.setSpeed(10);
}

void loop() {
  while (Serial.available() > 0) {
    String str = Serial.readString();
    if (str == "") {
    } else if (str == "go\n") {
      stepper1.step(4.4 * stepsScale / noSteps);
      delay(500);
    } else {
      noSteps = (str.substring(0, str.length() - 1)).toInt();
    }
  }
}
