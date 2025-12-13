CC = g++
CFLAGS = -Wall -std=c++17
TARGET = ../../morph

all: $(TARGET)

$(TARGET): main.cpp fox_vm.cpp
	$(CC) $(CFLAGS) -o $(TARGET) main.cpp fox_vm.cpp

clean:
	rm -f $(TARGET)
