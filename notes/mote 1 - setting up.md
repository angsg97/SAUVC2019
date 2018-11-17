# SAUVC 2019

# Setting up Odroid-XU4

We choose Ubuntu mate 16.04 as the platform to run our codes.

## Setting up system

### Install system

Ubuntu mate 16.04 for Odroid - XU4 can be found on its website : https://odroid.in/ubuntu_16.04lts/

and the tool recommended by the official site is etcher which can be found on https://www.balena.io/etcher/

If you are familiar with setting up raspberry pi, then this process is easy for you.

Ubuntu 16.04 for odroid does not require you to set your account and password when you install it, it is set by default and both are odroid.

### Find out IP Address

There is a way for you to help you find out the IP address of the host without using a monitor.

(If you are using the Modem provided)

find your IP first and as ssh open use 22 as the default port. So we use nmap to scan all the IPs port 22. (we assume the only difference between your computer and the Odroid is the last a few digits)

~~~
nmap -p 22 192.168.0.*
~~~

And we get 

~~~
Starting Nmap 7.60 ( https://nmap.org ) at 2018-11-13 22:09 +08
Nmap scan report for 192.168.0.102
Host is up (0.076s latency).

PORT   STATE SERVICE
22/tcp open  ssh

Nmap scan report for luo-sutd-sg (192.168.0.105)
Host is up (0.00033s latency).

PORT   STATE  SERVICE
22/tcp closed ssh

Nmap scan report for _gateway (192.168.0.254)
Host is up (0.020s latency).

PORT   STATE  SERVICE
22/tcp closed ssh

Nmap done: 256 IP addresses (3 hosts up) scanned in 20.49 seconds
~~~

The only one with port 22 open is the one which we are looking for, which is 192.168.0.102 here.

After ssh inside, it is recommended to set static IP address.

## Setting up opencv

We choose to compile the opencv instead of installing it from conda sources.

And we chose opencv version 3.4

### Preparation

To simplify our work we can create a install file instead of copying them everytime

~~~
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install build-essential cmake pkg-config
sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get install libxvidcore-dev libx264-dev
sudo apt-get install libgtk2.0-dev
sudo apt-get install libatlas-base-dev gfortran
sudo apt-get install python2.7-dev python3-dev
~~~

cp the commands upwords in to a file called install.sh

~~~
sudo chmod +x install.sh
sudo ./install.sh
~~~

Download both opencv file from github and unzip them 

~~~
cd ~ # go to home directory
wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.4.0.zip # Download opencv
wget -O opencv_contrib.zip https://github.com/Itseez/opencv_contrib/archive/3.4.0.zip # opencv_contrib is also needed
unzip opencv.zip
unzip opencv_contrib.zip
~~~

create a virtual environment

~~~
wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py # install the latest pip
sudo pip install virtualenv virtualenvwrapper
echo -e "\n# virtualenv and virtualenvwrapper" >> ~/.profile  # updating ~/.profile
echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.profile
echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.profile
source ~/.profile
mkvirtualenv cv -p python3 # create a virtual environment
source ~/.profile
workon cv # use workon to change the environment you are working on
~~~

### Compile and install opencv

We install numpy first and start up our build

~~~
pip install numpy
cd ~/opencv-3.1.0/
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D INSTALL_PYTHON_EXAMPLES=ON \
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib-3.4.0/modules \
    -D BUILD_EXAMPLES=ON ..
~~~

After you have done it successfully

Now we are ready to compile OpenCV, this process can take more than half an hour, so please be patient and get yourself a cup of coffee. Take care of the Odroid and try to cool it down.

The number after j stands for the number of the cores that you want to use together to compile opencv

~~~
make -j8
sudo make install
sudo ldconfig
~~~

### Finish installing Opencv

~~~
cd ~/.virtualenvs/cv/lib/python3.5/site-packages/
sudo mv cv2.cpython-35m-arm-linux-gnueabihf.so cv2.so
cd ~/.virtualenvs/cv/lib/python3.5/site-packages/
ln -s /usr/local/lib/python3.5/site-packages/cv2.so cv2.so
~~~

### Testing 

~~~
source ~/.profile
workon cv
python
import cv2
cv2.__version__
~~~

done