# ##########################################################################
# LZ4 examples - Makefile
# Copyright (C) Yann Collet 2011-2014
#
# GPL v2 License
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# You can contact the author at :
#  - LZ4 source repository : https://github.com/Cyan4973/lz4
#  - LZ4 forum froup : https://groups.google.com/forum/#!forum/lz4c
# ##########################################################################
# This makefile compile and test
# example programs, using (mostly) LZ4 streaming library,
# kindly provided by Takayuki Matsuoka
# ##########################################################################

CFLAGS ?= -O3
CFLAGS += -std=gnu99 -Wall -Wextra -Wundef -Wshadow -Wcast-align -Wstrict-prototypes

ifeq ($(WITH_IPP), yes)
CFLAGS += -DWITH_IPP -I$(IPPROOT)/include
ifeq ($(ARCH), ia32)
CFLAGS += -m32
endif
#
# System configuration detection
#
SYSTEM_SFX := $(shell uname)
ifeq ($(SYSTEM_SFX),Darwin)
	G_SYSTEM := macOS
else
	G_SYSTEM := Linux
endif

ifeq ($(G_SYSTEM), macOS)
        IPPLIBS64 := $(IPPROOT)/lib/libippdc.a $(IPPROOT)/lib/libipps.a $(IPPROOT)/lib/libippcore.a
else
        IPPLIBS64 := $(IPPROOT)/lib/intel64/libippdc.a $(IPPROOT)/lib/intel64/libipps.a $(IPPROOT)/lib/intel64/libippcore.a
endif

# For linking to dynamic libraries
#IPPLIBS64 = -L$(IPPROOT)/lib/intel64 -lippdc -lipps -lippcore

ifneq ($(G_SYSTEM), macOS)
        IPPLIBS32 = $(IPPROOT)/lib/ia32/libippdc.a $(IPPROOT)/lib/ia32/libipps.a $(IPPROOT)/lib/ia32/libippcore.a
else
        IPPLIBS32 = $(IPPLIBS64)
endif
# For linking to dynamic libraries
# IPPLIBS32 = -L$(IPPROOT)/lib/ia32 -lippdc -lipps -lippcore

ifeq ($(ARCH), intel64)
	IPPLIBS = $(IPPLIBS64)
else
	IPPLIBS = $(IPPLIBS32)
endif
endif

FLAGS  := -I../lib $(CPPFLAGS) $(CFLAGS) $(LDFLAGS)

TESTFILE= Makefile
LZ4DIR := ../lib
LZ4 = ../programs/lz4
# Define *.exe as extension for Windows systems
ifneq (,$(filter Windows%,$(OS)))
EXT =.exe
VOID = nul
else
EXT =
VOID = /dev/null
endif


default: all

all: printVersion doubleBuffer dictionaryRandomAccess ringBuffer ringBufferHC lineCompress frameCompress

printVersion: $(LZ4DIR)/lz4.c printVersion.c
ifeq ($(WITH_IPP), yes)
	$(CC)      $(FLAGS) $^ -o $@$(EXT) $(IPPLIBS)
else
	$(CC)      $(FLAGS) $^ -o $@$(EXT)
endif

doubleBuffer: $(LZ4DIR)/lz4.c blockStreaming_doubleBuffer.c
ifeq ($(WITH_IPP), yes)
	$(CC)      $(FLAGS) $^ -o $@$(EXT) $(IPPLIBS)
else
	$(CC)      $(FLAGS) $^ -o $@$(EXT)
endif

dictionaryRandomAccess: $(LZ4DIR)/lz4.c dictionaryRandomAccess.c
ifeq ($(WITH_IPP), yes)
	$(CC)      $(FLAGS) $^ -o $@$(EXT) $(IPPLIBS)
else
	$(CC)      $(FLAGS) $^ -o $@$(EXT)
endif

ringBuffer  : $(LZ4DIR)/lz4.c blockStreaming_ringBuffer.c
ifeq ($(WITH_IPP), yes)
	$(CC)      $(FLAGS) $^ -o $@$(EXT) $(IPPLIBS)
else
	$(CC)      $(FLAGS) $^ -o $@$(EXT)
endif

ringBufferHC: $(LZ4DIR)/lz4.c $(LZ4DIR)/lz4hc.c HCStreaming_ringBuffer.c
ifeq ($(WITH_IPP), yes)
	$(CC)      $(FLAGS) $^ -o $@$(EXT) $(IPPLIBS)
else
	$(CC)      $(FLAGS) $^ -o $@$(EXT)
endif

lineCompress: $(LZ4DIR)/lz4.c blockStreaming_lineByLine.c
ifeq ($(WITH_IPP), yes)
	$(CC)      $(FLAGS) $^ -o $@$(EXT) $(IPPLIBS)
else
	$(CC)      $(FLAGS) $^ -o $@$(EXT)
endif

frameCompress: frameCompress.c
ifeq ($(WITH_IPP), yes)
	$(CC)      $(FLAGS) $^ -o $@$(EXT) $(LZ4DIR)/liblz4.a $(IPPLIBS)
else
	$(CC)      $(FLAGS) $^ -o $@$(EXT) $(LZ4DIR)/liblz4.a
endif

compressFunctions: $(LZ4DIR)/lz4.c compress_functions.c
ifeq ($(WITH_IPP), yes)
	$(CC)      $(FLAGS) $^ -o $@$(EXT) -lrt $(IPPLIBS)
else
	$(CC)      $(FLAGS) $^ -o $@$(EXT) -lrt
endif

simpleBuffer: $(LZ4DIR)/lz4.c simple_buffer.c
ifeq ($(WITH_IPP), yes)
	$(CC)      $(FLAGS) $^ -o $@$(EXT) $(IPPLIBS)
else
	$(CC)      $(FLAGS) $^ -o $@$(EXT)
endif

test : all
	./printVersion$(EXT)
	./doubleBuffer$(EXT) $(TESTFILE)
	./dictionaryRandomAccess$(EXT) $(TESTFILE) $(TESTFILE) 1100 1400
	./ringBuffer$(EXT)   $(TESTFILE)
	./ringBufferHC$(EXT) $(TESTFILE)
	./lineCompress$(EXT) $(TESTFILE)
	./frameCompress$(EXT) $(TESTFILE)
	$(LZ4) -vt $(TESTFILE).lz4

clean:
	@rm -f core *.o *.dec *-0 *-9 *-8192 *.lz4s *.lz4 \
	 printVersion$(EXT) doubleBuffer$(EXT) dictionaryRandomAccess$(EXT) \
	 ringBuffer$(EXT) ringBufferHC$(EXT) lineCompress$(EXT) frameCompress$(EXT) \
	 compressFunctions$(EXT) simpleBuffer$(EXT)
	@echo Cleaning completed
