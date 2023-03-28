# Práctica 3 con Interrupciones GPIO
Funcionamiento: Encendido y apagado de un LED (GPIO 5) mediante la pulsación de un botón (GPIO 19).
Cuidado: Para poder probar la práctica hay que cambiar antes las rutas que vienen en los scripts.

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

3) A continuación, pondremos un breakpoint en la línea 202 para poder ver el tratamiento de las interrupciones mediante GPIO:
> b 99

> c

4) Para comprobar que el programa esté funcionando correctamente, utilizaremos el terminal de qemu-rpip-gpio y primeramente tenemos asegurarnos de que el gpio 19 esté a 0:
> set 19 0

Cada vez que cambiemos el valor del GPIO 19 de 0 a 1 el valor del GPIO 5 cambiará:
> set 19 1

> get 5
