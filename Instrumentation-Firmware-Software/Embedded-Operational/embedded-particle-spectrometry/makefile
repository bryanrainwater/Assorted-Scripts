# the compiler to use
CC = clang

# compiler flags:
#  -g    adds debugging information to the executable file
#  -Wall turns on most, but not all, compiler warnings
CFLAGS  = -g -Ofast -Wall
#CFLAGS  = -g -O0 -Wall
  
# the name to use for both the target source file, and the output file:
TARGET = ptof
  
all: $(TARGET)
  
$(TARGET): $(TARGET).o sqrt.o mie.o ini.o beaglelogic.o
	$(CC) $(CFLAGS) -o $(TARGET) $(TARGET).o sqrt.o mie.o ini.o beaglelogic.o 

$(TARGET).o: $(TARGET).c
	$(CC) -c $(CFLAGS) -o ptof.o ptof.c

sqrt.o: sqrt.c
	$(CC) -c $(CFLAGS) -o sqrt.o sqrt.c

mie.o: mie.c
	$(CC) -c $(CFLAGS) -o mie.o mie.c

ini.o: ini.c
	$(CC) -c $(CFLAGS) -o ini.o ini.c

beaglelogic.o: beaglelogic.c
	$(CC) -c $(CFLAGS) -o beaglelogic.o beaglelogic.c
