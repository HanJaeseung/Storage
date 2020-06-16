CC = gcc
CFLAGS = -fPIC
LDFLAGS = -shared
INCLUDES = -I/usr/include/python2.7
#INCLUDES = -I/usr/include/python3.5m
LIBRARY = -lpython2.7 -lkms
#LIBRARY = -lpython3.5m -lkms
LIBRARY_PATH = -L.
TARGET = main

RM= rm -f
.PHONY: all clean

all: $(TARGET)

clean:
	$(RM) *.o *.so core $(TARGET)

main: libkms.so
	$(CC) main.c $< -o $@ $(INCLUDES) $(LIBRARY) $(LIBRARY_PATH)

libkms.so: kms.c kms.h
	$(CC) $< $(CFLAGS) $(LDFLAGS) $(INCLUDES) -o $@
