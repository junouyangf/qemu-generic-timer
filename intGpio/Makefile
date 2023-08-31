
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

intGpio.o : intGpio.c
	$(ARMGNU)-gcc $(COPS) $(CFLAGS) -c intGpio.c -o intGpio.o

kernel8.img : memmap vectors.o intGpio.o 
	$(ARMGNU)-ld vectors.o intGpio.o -T memmap -o intGpio.elf
	$(ARMGNU)-objdump -D intGpio.elf > intGpio.list
	$(ARMGNU)-objcopy --srec-forceS3 intGpio.elf -O srec intGpio.srec
	$(ARMGNU)-objcopy intGpio.elf -O binary kernel8.img


