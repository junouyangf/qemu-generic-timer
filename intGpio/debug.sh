#!/bin/sh

gdb-multiarch  intGpio.elf  -ex "target remote localhost:1234"


