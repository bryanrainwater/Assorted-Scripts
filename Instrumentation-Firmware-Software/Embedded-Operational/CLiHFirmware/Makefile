#
# Makefile
# Copyright (c) 2014 by Diamond Systems.
#
# Make file to build Demo application
#

APPName = dsm
LIB =-L ./Common/ -ldscud-8.0.0 -lm -lpthread
INC =-I ./Common/

all: $(APPName).o

$(APPName).o:
	#gcc -o $(APPName) $(APPName).c $(INC) $(LIB)
	gcc -shared -Wl,-soname,$(APPName) -o $(APPName).so -fPIC $(APPName).c $(INC) $(LIB)
	#gcc -shared -fno-exceptions -Wall -Wextra -Wl,_ZdaPv,-soname,$(APPName) -o $(APPName).so -fPIC $(APPName).cpp $(INC) $(LIB)
	#cp $(APPName) ../Executables

clean:
	rm -f $(APPName).o $(APPName)
