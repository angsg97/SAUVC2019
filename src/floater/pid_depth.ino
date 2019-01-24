#include <Wire.h>
#include <Servo.h>
#include <SparkFun_MS5803_I2C.h>
#include <Servo.h>
Servo ESC1; //up
Servo ESC2; //up
Servo ESC3; //faulty esc does not run below and at 1500
Servo ESC4;
//#define MOTOR_AA 10 // Motor A Analog Pin    the pin to control speed (has to be a PWM pin)
//#define MOTOR_BA 3
//#define MOTOR_CA 5    //up add a forward movement for the craft
//#define MOTOR_DA 11
//1000-2000 stops at 1000, max speed at 2000


MS5803 sensor(ADDRESS_HIGH);

float temp;
float pressure_abs, pressure_baseline, outputdepth,altitude_delta,error1,error2,new_speed;
int const MIN_HEIGHT =-4;
int const MAX_HEIGHT= -8;

// PID CONSTANTS
float Kp, Ki, Kd;
int i,n;
int previousTime;
float lastDepth;
float depth;
int feedback;
float temperature_c;
float outputError;

void setup() {
  // Initialize pin Mode
  Serial.begin(9600);
  sensor.reset();
  sensor.begin();
    
  pressure_baseline = sensor.getPressure(ADC_4096);

  ESC1.attach(10);
  ESC2.attach(3);//Adds ESC to certain pin. IDK why it doesnt work when i put it in loop.
  ESC3.attach(5);
  ESC4.attach(11);
  delay(2000); //give time to connect the battery
  ESC1.writeMicroseconds(2000); //Calibrate max throttle first, 2beeps on success.
  ESC2.writeMicroseconds(2000);
  ESC3.writeMicroseconds(2000); 
  ESC4.writeMicroseconds(2000);
  delay(3000); //give time to calibrate max throttle
  ESC1.writeMicroseconds(1000); //Calibrate min throttle next, 3beeps on success.
  ESC2.writeMicroseconds(1000); 
  ESC3.writeMicroseconds(1000); //Calibrate min throttle next, 3beeps on success.
  ESC4.writeMicroseconds(1000); 
  Serial.print("5seconds is over\n"); //Long beep for calibration over
  delay(2000);

}

void loop() {
  Serial.println("beginning loop");
  PIDconstants();
  // Read temperature from the sensor in deg C. This operation takes about 
  temperature_c = sensor.getTemperature(CELSIUS, ADC_512);
  
   // Read pressure from the sensor in mbar.
  pressure_abs = sensor.getPressure(ADC_4096);
  Serial.println("pressureabs:");
  Serial.println(pressure_abs);
  
  // Taking our baseline pressure at the beginning we can find an approximate
  // change in altitude based on the differences in pressure.   
  altitude_delta = altitude(pressure_abs , pressure_baseline);
  //depth=altitude_delta/1800*500;  //in metres with metrics calculated from within 150m https://www.mide.com/pages/air-pressure-at-altitude-calculator
  depth=altitude_delta;
  Serial.print("alttude delta");
  Serial.print(altitude_delta);
  Serial.print("\n");

 // Report values via UART
  //Serial.print("Altitude change (m) = ");
  //Serial.println(altitude_delta); 
  if (depth >  MIN_HEIGHT )
  {
    Serial.println("too shallow");
    error1 = readSensorError_min(depth);
    feedback=PID(error1);  //PID(&Input, &Output, &Setpoint, Kp, Ki, Kd, Direction) 
    Serial.println("feedback");
    Serial.println(feedback);
    new_speed=turnCalcMin(feedback);
    ESC1.writeMicroseconds(new_speed); //Calibrate max throttle first, 2beeps on success.
    ESC2.writeMicroseconds(new_speed);
    ESC3.writeMicroseconds(1600);   
    ESC4.writeMicroseconds(1600);

  }
  else if (depth < MAX_HEIGHT)
  {
    error2 = readSensorError_max(depth);
    //feedback=PID(error2);
    //new_speed=turnCalcMax(feedback);
    Serial.println("too deep");
    ESC1.writeMicroseconds(1000); //Calibrate max throttle first, 2beeps on success.
    ESC2.writeMicroseconds(1000);
    ESC3.writeMicroseconds(1600);   //test, goes straight
    ESC4.writeMicroseconds(1600);
  }
  else{
    Serial.println("above water height");
    ESC1.writeMicroseconds(1000);   //test, goes straight
    ESC2.writeMicroseconds(1000);  
    ESC3.writeMicroseconds(1600);   
    ESC4.writeMicroseconds(1600);
  }

  delay(2000);

}
//-----------------------------------------PID-----------------------------------------------

void PIDconstants(void)
{
  Kp = 20;    // RANDOM VALUES
  Ki = 10;
  Kd = 100;
}

float readSensorError_min(float depth) {
  return depth - MIN_HEIGHT;      // Check for math
}

float readSensorError_max(float depth) {
  return MAX_HEIGHT - depth;      // Check for math

}

float PID(float depth)
{
  float depthSum;
  float differentialdepth;  

  depthSum += depth;
  int currentTime = millis();
  differentialdepth = (depth - lastDepth)/(currentTime - previousTime);
  //Serial.println (depthSum);
  lastDepth = depth;
  previousTime = currentTime;

  /*
  if (abs(depth) > 1)   // IGNORE CRAZY depthS
  {
    depthSum = 0;
  }
  */
  
  float proportional = depth * Kp;  // Calculate the components of the PID
  float integral = depthSum * Ki;
  float differential = differentialdepth * Kd;
  double output = proportional + integral + differential;  // Calculate the result

  return output; 
}

float turnCalcMin(float feedback){
// Restrict feedback to [0, maxSpeed]
  if (feedback <2) {  //map maxspeedto distance
    new_speed=feedback/1*2000+1000; // feedback/distance*maxspeed+minspeed
  }
  else{
    new_speed=2000;
  }

  return new_speed;
}


//---------------------------------setmotors---------------------

//----------------------------depthsensor-----------------------------
double altitude(double P, double P0)
// Given a pressure measurement P (mbar) and the pressure at a baseline P0 (mbar),
// return altitude (meters) above baseline.
{
  return(44330.0*(1-pow(P/P0,1/5.255)));
}
