# Práctica 3 con Generic Timer
Cuidado: Para poder probar la práctica hay que cambiar antes las rutas que vienen en los scripts.

El Generic Timer puede programar eventos y generar interrupciones basadas en el valor incrementado de un contador.
En el caso de la Raspberry Pi 3b, tenemos un procesador con 4 cores, los cuales poseen cada uno de ellos un conjunto de timers:
- Un temporizador físico no seguro EL1. 
- Un temporizador físico seguro EL2.
- Un temporizador físico EL3.
- Un temporizador virtual. → Usamos este

Datasheet BCM2837
>https://datasheets.raspberrypi.com/bcm2836/bcm2836-peripherals.pdf

Datasheet Procesador ARM Cortex-A53
>https://developer.arm.com/documentation/ddi0500/j/Generic-Timer/Generic-Timer-register-summary/AArch64-Generic-Timer-register-summary?lang=en

#Depuración
1) Abrir 3 terminales
> ./qemu-rpi-gpio

>./run.sh

>./debug.sh

2) En el terminal de depuración, pondremos un breakpoint para acceder al main:
> b main

> c

3) A continuación, pondremos un breakpoint en la línea 202 para poder ver el tratamiento de las interrupciones periódicas:
> b 202

> c

4) Para comprobar que el programa esté funcionando correctamente, utilizaremos el terminal de qemu-rpip-gpio y leeremos el valor del GPIO 6, el cual cada vez que se produce la interrupción alterna su valor (true o false).
> get 6
