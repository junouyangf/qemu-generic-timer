# Programa bare-metal con System Timer
Funcionamiento: De manera periódica, la salida correspondiente al GPIO 6, alternará. Así, si asignamos a un LED el GPIO 6, este de manera periódica, se encenderá o apagará.

Datasheet BCM2837
>https://datasheets.raspberrypi.com/bcm2836/bcm2836-peripherals.pdf

# Depuración
1) En la aplicación de interfaz de usuario, añadiremos un led asignado al GPIO 6 y ejecutamos la opción de depuración.

2) A continuación, pondremos un breakpoint en la línea 122 para poder ver el tratamiento de las interrupciones periódicas:
> b 133

> c

3) Para comprobar que el programa esté funcionando correctamente, simplemente de manera periódica se generará la interrupción y se cambiará el valor del GPIO, y por ende, el LED se encenderá o apagará.
