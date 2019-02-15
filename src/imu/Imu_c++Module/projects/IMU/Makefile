CXX = g++
INCLUDES = -I ../../include
CPPFLAGS = -Wall

SOURCES = main.cpp

all: SAUVC

clean:
	rm -f main.o
	rm -f SAUVC
	cd ../.. && make clean

SAUVC: main.o ../../build/bin/libvncxx.a
	$(CXX) -o SAUVC main.o -L ../../build/bin -lvncxx -lpthread

../../build/bin/libvncxx.a:
	cd ../.. && make

main.o: main.cpp
	$(CXX) $(CPPFLAGS) $(INCLUDES) -c $< -o $@

