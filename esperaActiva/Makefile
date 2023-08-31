
ARMGNU ?= ~/gcc-arm-10.3-2021.07-x86_64-aarch64-none-elf/bin/aarch64-none-elf


PLATFORM = raspi

AOPS = --warn --fatal-warnings
COPS = -Wall -O2 -nostdlib -nostartfiles -ffreestanding 

CFLAGS = -O0 -g -std=gnu99 -Werror -D__$(PLATFORM)__ -DRASPBERRY_PI -fno-builtin 
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
	$(ARMGNU)-as $(AOPS) $(ASFLAGS)  vectors.s -o vectors.o

esperaActiva.o : esperaActiva.c
	$(ARMGNU)-gcc $(COPS) $(CFLAGS) -c esperaActiva.c -o esperaActiva.o

kernel8.img : memmap vectors.o esperaActiva.o 
	$(ARMGNU)-ld vectors.o esperaActiva.o -T memmap -o esperaActiva.elf
	$(ARMGNU)-objdump -D esperaActiva.elf > esperaActiva.list
	$(ARMGNU)-objcopy --srec-forceS3 esperaActiva.elf -O srec esperaActiva.srec
	$(ARMGNU)-objcopy esperaActiva.elf -O binary kernel8.img


