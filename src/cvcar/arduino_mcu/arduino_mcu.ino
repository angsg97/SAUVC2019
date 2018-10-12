#define MOTOR_AA 5
#define MOTOR_AD 4
#define MOTOR_AI 1

#define MOTOR_BA 6
#define MOTOR_BD 7
#define MOTOR_BI 1

void setMotor(int powerA, int powerB) {
  if (MOTOR_AI)
    powerA = -powerA;
  digitalWrite(MOTOR_AD, powerA < 0);
  analogWrite(MOTOR_AA, powerA > 0 ? powerA : powerA + 255);
  if (MOTOR_BI)
    powerB = -powerB;
  digitalWrite(MOTOR_BD, powerB < 0);
  analogWrite(MOTOR_BA, powerB > 0 ? powerB : powerB + 255);
}

void setup() {
  pinMode(MOTOR_AA, OUTPUT);
  pinMode(MOTOR_AD, OUTPUT);
  pinMode(MOTOR_BA, OUTPUT);
  pinMode(MOTOR_BD, OUTPUT);

  Serial.begin(115200);
  Serial.setTimeout(10);
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readString();
    int separator = input.indexOf(" ");
    int valueA = input.substring(0, separator).toInt();
    int valueB = input.substring(separator).toInt();
    setMotor(valueA, valueB);
  }
}
