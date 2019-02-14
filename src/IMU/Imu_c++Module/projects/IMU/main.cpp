#include<iostream>
#include<stdio.h>
#include<stdio.h>
#include "vn/sensors.h"
#include "vn/thread.h"

using namespace std;
using namespace vn::math;
using namespace vn::sensors;
using namespace vn::protocol::uart;
using namespace vn::xplat;


// Declaring method, will be used in setting up asynchronous communication with VnSensor
void asciiAsyncMessageReceived(void* userData, Packet& p, size_t index);



int main(int argc, char *argv[])
{

//initializing port connections with VnSensor
const string SensorPort = "/dev/ttyUSB0";                  
const uint32_t SensorBaudrate = 115200;

//creating a VnSEnsor object
VnSensor vs;
vs.connect(SensorPort, SensorBaudrate);

//we will send tell the used which model of VnSensor are they using
//string mn = vs.readModelNumber();
//cout<< "Model number :"<< mn<< endl;

//some gyro orientation reading from the imu
//vec3f ypr = vs.readYawPitchRoll();
//cout << "Current Yaw , pitch and roll:" << ypr << endl;
//we can use yaw as our heading 

//the method of getting YPR With the method above is slow, due to sending command and then receiving it back
// to improve this lag time, we will configure the library to alert us when any asynchronous data is sent. 
vs.writeAsyncDataOutputType(VNYMR);
//AsciiAsync asyncType = vs.readAsyncDataOutputType();
//cout << "ASCII Async Type: " << asyncType << endl;
//fflush(stdout);

//define a which has the appropirate signature(byte message) to receive notifications
vs.registerAsyncPacketReceivedHandler(NULL, asciiAsyncMessageReceived);

//sleep allows the asynchronous callback method to receive and display yaw, pitch and roll packets.
//cout<<"Starting sleep......"<<endl;
//fflush(stdout);

Thread::sleepSec(10000);
//this counts in seconds
// this will be the length of time the imu will be on
//to unregister our callback method
vs.unregisterAsyncPacketReceivedHandler();
vs.disconnect();
return 0 ;

}


void asciiAsyncMessageReceived(void* userData, Packet& p, size_t index)
{
        // Make sure we have an ASCII packet and not a binary packet.
        if (p.type() != Packet::TYPE_ASCII)
                return;

        // Make sure we have a VNYMR data packet.
        if (p.determineAsciiAsyncType() != VNYMR)
                return;

        // We now need to parse out the yaw, pitch, roll data, magnetic, acceleration, angular Rate
        vec3f ypr, mag, accel, angularRate;
	p.parseVNYMR(&ypr, &mag, &accel, &angularRate);

        //cout << "[Found VNYMR Packet]" << endl;
        cout << "  YawPitchRoll: " << ypr << endl;
        fflush(stdout);
        cout << "  Magnetic: " << mag << endl;
        fflush(stdout);
        cout << "  Acceleration: " << accel << endl;
        fflush(stdout);
        cout << "  Angular Rate: " << angularRate << endl;
        fflush(stdout);
}


