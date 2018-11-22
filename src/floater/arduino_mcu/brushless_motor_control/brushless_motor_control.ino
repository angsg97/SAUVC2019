#include <Servo.h>

Servo servoL;
Servo servoR;

int servo1 = 5;
int servo2 = 6;
//here you declare your  which pin is connected to which servo
//servo1 is for the left servo
//servo 2 is for the right servo


//for continuous servo or motor 0 counterclockwise, 90 is stationary ,  180 is clockwise
void straight(){
  servoL.write(180);
  servoR.write(180);
  delay(2000);
}

//call this to go right
void right(){
  servoL.write(180);
  servoR.write(90);
}

// call this to go left
void left(){
  servoL.write(90);
  servoR.write(180);
}

// call this to stop
void stopp(){
  servoL.write(90);
  servoR.write(90);
}

// call this to reverse
void reverse(){
  servoL.write(0);
  servoR.write(0);
}



void setup() {
  // put your setup code here, to run once:
servoL.attach(servo1);
servoR.attach(servo2);
Serial.begin(9600);
}
void loop() {
  // put your main code here, to run repeatedly:
if(Serial.available() > 0) {
  byte choice = Serial.read();
  
  switch(choice){
    case 's':
    straight();
    break;

    case 'r':
    right();
    break;

    case 'l':
    left();
    break;

    case 'x':
    stopp();
    break;

    case 'b':
    reverse();
    break;
  }
 }
}
