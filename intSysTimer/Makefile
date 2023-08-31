
ARMGNU ?= ~/gcc-arm-10.3-2021.07-x86_64-aarch64-none-elf/bin/aarch64-none-elf


PLATFORM = raspi

AOPS = --warn --fatal-warnings
COPS = -Wall -O2 -nostdlib -nostartfiles -ffreestanding 

CFLAGS = -O0 -g -std=gnu99  -D__$(PLATFORM)__ -DRASPBERRY_PI -fno-builtin 
ASFLAGS = -g


gcc : kernel8.img

all : gcc

clean :
	rm -f *.o
	rm -f *.bin
	rm -f *.srec
	rm -f *.elf
	rm -f *.list
	rm -f *.img

vectors.o : vectors.s
	$(ARMGNU)-as  $(ASFLAGS)  vectors.s -o vectors.o

intSysTimer.o : intSysTimer.c
	$(ARMGNU)-gcc $(COPS) $(CFLAGS) -c intSysTimer.c -o intSysTimer.o

kernel8.img : memmap vectors.o intSysTimer.o 
	$(ARMGNU)-ld vectors.o intSysTimer.o -T memmap -o intSysTimer.elf
	$(ARMGNU)-objdump -D intSysTimer.elf > intSysTimer.list
	$(ARMGNU)-objcopy --srec-forceS3 intSysTimer.elf -O srec intSysTimer.srec
	$(ARMGNU)-objcopy intSysTimer.elf -O binary kernel8.img


