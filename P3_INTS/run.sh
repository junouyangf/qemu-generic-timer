#!/bin/sh

~/qemu-master/build/qemu-system-arm  -M raspi0 -kernel kernel.elf -s -S -nographic -qtest unix:/tmp/tmp-gpio.sock 
	
