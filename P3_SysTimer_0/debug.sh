#!/bin/sh

arm-none-eabi-gdb kernel.elf -ex "target remote localhost:1234"


