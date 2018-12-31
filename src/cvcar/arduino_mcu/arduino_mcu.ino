#define MOTOR_AA 5 // Motor A Analog Pin    the pin to control speed (has to be a PWM pin)
#define MOTOR_AD 4 // Motor A Digital Pin   the pin to control direction
#define MOTOR_AI 1 // Motor A Inverted

#define MOTOR_BA 6
#define MOTOR_BD 7
#define MOTOR_BI 1

void setMotor(int powerA, int powerB) {
  if (MOTOR_AI)
    powerA = -powerA;
  /* If power is positive
   *   Digital pin is LOW, and the duty ratio of the analog pin is the same as power
   *   So, power/255 of time, A > D, the motor rotate forward
   * If power is negative
   *   Digital pin is HIGH, and the duty ratio of the analog pin is (255 - power)
   *   So, power/255 of time, A < D, the motor rotate backward
   */
  digitalWrite(MOTOR_AD, powerA < 0);
  analogWrite(MOTOR_AA, powerA > 0 ? powerA : powerA + 255);
  if (MOTOR_BI)
    powerB = -powerB;
  digitalWrite(MOTOR_BD, powerB < 0);
  analogWrite(MOTOR_BA, powerB > 0 ? powerB : powerB + 255);
}

void setup() {
  // Initialize pin Mode
  pinMode(MOTOR_AA, OUTPUT);
  pinMode(MOTOR_AD, OUTPUT);
  pinMode(MOTOR_BA, OUTPUT);
  pinMode(MOTOR_BD, OUTPUT);

  // Initialize serial
  Serial.begin(115200);
  Serial.setTimeout(10); // Set the time out for readString
}

void loop() {
  if (Serial.available()) {
    // read command from SBC, should be two numbers separated by a space. eg."80 120"
    String input = Serial.readString();
    int separator = input.indexOf(" ");
    int valueA = input.substring(0, separator).toInt(); // convert string to int, range is [-255, 255]
    int valueB = input.substring(separator).toInt();
    setMotor(valueA, valueB);
  }
}
