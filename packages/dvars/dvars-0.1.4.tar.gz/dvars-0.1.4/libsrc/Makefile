# Compile the shared library $(LNAME) from dars.c and roesset_quake.c
# Designed to work on Linux and create native builds for Linux or
# cross-platform builds for Windows using the MinGW-w64 toolchain.
# To use this Makefile, ensure you have the MinGW-w64 toolchain installed
# and available in your PATH,
# /usr/i686-w64-mingw32/bin for 32-bit Windows compilation or
# /usr/x86_64-w64-mingw32/bin for 64-bit Windows compilation.

# Run make with the PLAT variable set to specify the platform.
# For example:
# make PLAT=win_amd64
# or only make for native compilation.

.PHONY: all clean install

ifeq ($(PLAT),win_amd64)
  # For 64-bit Windows compilation
  CC=/usr/bin/x86_64-w64-mingw32-gcc
  LIBSUFFIX=.pyd
  EXESUFFIX=.exe
  #LDFLAGS=-static-libgcc
else ifeq ($(PLAT),win-amd64)
  # For 64-bit Windows compilation
  CC=/usr/bin/x86_64-w64-mingw32-gcc
  LIBSUFFIX=.pyd
  EXESUFFIX=.exe
  #LDFLAGS=-static-libgcc
else ifeq ($(PLAT),win32)
  # For 32-bit Windows compilation
  CC=/usr/bin/i686-w64-mingw32-gcc
  LIBSUFFIX=.pyd
  EXESUFFIX=.exe
  #LDFLAGS=-static-libgcc
else
  # For native compilation (Linux)
  CC=gcc
  LIBSUFFIX=.so
endif

#CFLAGS=-ggdb -O0 -Wall
CFLAGS= -O3 -Wall
CPPFLAGS=
LDFLAGS=
LNAME=libdars_$(PLAT)$(LIBSUFFIX)
ENAME=test$(EXESUFFIX)

SHELL=bash

all: $(LNAME) $(ENAME)

# Build the shared library
# Do not create object files separately, as to avoid issues with cross-compilation.
$(LNAME): dars.c roesset_quake.c
	$(CC) $(CFLAGS) $(CPPFLAGS) $(LDFLAGS) \
		-shared -fPIC -o $(LNAME) dars.c roesset_quake.c

# Build the executable test program
$(ENAME): $(LNAME) dars.h test.c
	$(CC) $(CFLAGS) $(CPPFLAGS) $(LDFLAGS) -o test test.c ./$(LNAME) -lm

clean:
	-rm *.o
	-rm libdars*.* 
	-rm test{,.exe}

install: $(LNAME)
	@echo "installing $(LANME) to ../dvars/dars"
	install -m 644 $(LNAME) ../dvars/dars/

