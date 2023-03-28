
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

P3_1.o : P3_1.c
	$(ARMGNU)-gcc $(COPS) $(CFLAGS) -c P3_1.c -o P3_1.o

kernel8.img : memmap vectors.o P3_1.o 
	$(ARMGNU)-ld vectors.o P3_1.o -T memmap -o P3_1.elf
	$(ARMGNU)-objdump -D P3_1.elf > P3_1.list
	$(ARMGNU)-objcopy --srec-forceS3 P3_1.elf -O srec P3_1.srec
	$(ARMGNU)-objcopy P3_1.elf -O binary kernel8.img


