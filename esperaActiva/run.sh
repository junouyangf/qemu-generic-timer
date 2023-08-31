#!/bin/sh

~/qemu-master/build/qemu-system-aarch64 -s -S -M raspi3b -kernel P3_1.elf -nographic -qtest unix:/tmp/tmp-gpio.sock
	
