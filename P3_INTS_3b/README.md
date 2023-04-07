# Práctica 3 con System Timer
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

3) A continuación, pondremos un breakpoint en la línea 133 para poder ver el tratamiento de las interrupciones periódicas:
> b 133

> c

4) Para comprobar que el programa esté funcionando correctamente, utilizaremos el terminal de qemu-rpip-gpio y leeremos el valor del GPIO 6, el cual cada vez que se produce la interrupción alterna su valor (true o false).
> get 6

5) Debería producirse la interrupción periódicamente. (Actualmente solo lo realiza una sola vez)
