# Práctica 3 con ARM Timer
Cuidado: Para poder probar la práctica hay que cambiar antes las rutas que vienen en los scripts.

Para la implementación nos hemos basado en el manual que se nos adjuntó para la realización de la práctica.
Suponemos que el ARM Timer no es funcional ya que en la configuración del QEMU este no está implementado (en la línea 51 de /include/hw/arm/bcm2835_peripherals.h indica que armtmr es un UnimplementedDeviceState).

Datasheet BCM2837
>https://datasheets.raspberrypi.com/bcm2836/bcm2836-peripherals.pdf

# Depuración
1) Abrir 3 terminales
> ./qemu-rpi-gpio

>./run.sh

>./debug.sh

2) En el terminal de depuración, pondremos un breakpoint para acceder al main:
> b main

> c

3) A continuación, pondremos un breakpoint en la línea 138 para poder ver el tratamiento de las interrupciones periódicas:
> b 138

> c
