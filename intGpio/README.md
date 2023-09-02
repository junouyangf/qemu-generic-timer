# Programa bare-metal con Interrupciones GPIO
Funcionamiento: Encendido y apagado de un LED (GPIO 5) mediante la pulsación de un botón (GPIO 19).

Datasheet BCM2837
>https://datasheets.raspberrypi.com/bcm2836/bcm2836-peripherals.pdf

# Depuración
1) En la aplicación de interfaz de usuario, añadiremos un led asignado al GPIO 5 y un botón asignado al GPIO 19 y ejecutamos la opción de depuración.

2) A continuación, en el terminal de depuración, pondremos un breakpoint en la línea 89 para poder ver el tratamiento de las interrupciones generadas por GPIO:
> b 89
> c

3) Para comprobar que el programa esté funcionando correctamente, pulsaremos el botón correspondiente y en el terminal de depuración, al poner un breakpoint en el tratamiento de la interrupción, se detendrá para poder depurar dicho tratamiento.

4) Para continuar, simplemente introduciremos:
> c
>Y podremos observar cómo el LED se enciende o apaga.
