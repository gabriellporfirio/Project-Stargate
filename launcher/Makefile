# Builds the launcher with a MinGW-w64 cross compiler (Linux, macOS or MSYS2).
#
#   make            build/launcher.exe (renamed to "Pixel Media Checker.exe" when packaged)
#   make test       run the argument quoting tests with the host compiler
#   make wine-test  run the launcher under Wine against a fake interpreter
#   make clean

CROSS   ?= x86_64-w64-mingw32-
CC      := $(CROSS)gcc
WINDRES := $(CROSS)windres
HOSTCC  ?= cc
CFLAGS  ?= -O2 -std=c11 -Wall -Wextra -Werror
LDFLAGS ?= -s -static -Wl,--tsaware

BUILD   := build
SOURCES := src/launcher.c src/cmdline.c
HEADERS := src/cmdline.h src/version.h

.PHONY: all test wine-test clean

all: $(BUILD)/launcher.exe

$(BUILD)/launcher.res: launcher.rc launcher.manifest src/version.h ../app/assets/pixel.ico | $(BUILD)
	$(WINDRES) -O coff -i $< -o $@

$(BUILD)/launcher.exe: $(SOURCES) $(HEADERS) $(BUILD)/launcher.res
	$(CC) $(CFLAGS) -municode -mwindows -o $@ $(SOURCES) $(BUILD)/launcher.res -lshell32 $(LDFLAGS)

$(BUILD)/test_cmdline: tests/test_cmdline.c src/cmdline.c src/cmdline.h | $(BUILD)
	$(HOSTCC) -O2 -std=c11 -Wall -Wextra -Werror -Isrc -o $@ tests/test_cmdline.c src/cmdline.c

test: $(BUILD)/test_cmdline
	./$(BUILD)/test_cmdline

$(BUILD)/fake_python.exe: tests/fake_python.c | $(BUILD)
	$(CC) $(CFLAGS) -municode -o $@ $< -lshell32 $(LDFLAGS)

$(BUILD)/fake_pythonw.exe: tests/fake_python.c | $(BUILD)
	$(CC) $(CFLAGS) -municode -mwindows -o $@ $< -lshell32 $(LDFLAGS)

wine-test: $(BUILD)/launcher.exe $(BUILD)/fake_python.exe $(BUILD)/fake_pythonw.exe
	python3 tests/wine_test.py

$(BUILD):
	mkdir -p $@

clean:
	rm -rf $(BUILD)
