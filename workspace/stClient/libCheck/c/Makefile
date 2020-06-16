CC = gcc
CFLAGS = -fPIC
LDFLAGS = -shared
INCLUDES = -I/usr/include/python2.7
LIBRARY = -lpython2.7 -lkms
LIBRARY_PATH = -L.
TARGET = api_libCheck

RM= rm -f
.PHONY: all clean

all: $(TARGET)

clean:
	$(RM) *.o core $(TARGET)

api_libCheck: 
	$(CC) main.c libkms.so -o $@ $(INCLUDES) $(LIBRARY) $(LIBRARY_PATH)

