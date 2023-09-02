# Programa bare-metal de E/S mediante espera activa
Funcionamiento: El valor del GPIO 5 y 6 se alternarán dependiendo del botón que pulsemos (GPIO 19 y 20). Si pulsamos el botón correspondiente al GPIO 19, el valor del GPIO 5 y 6 cambiarán, es decir si la salida del GPIO 5 es 0, cambiará a 1,
y si el valor del GPIO 6 es 1, cambiará a 0. Por otro lado, si pulsamos el botón correspondiente al GPIO 20, únicamente el valor del GPIO 6 cambiará.

Datasheet BCM2837
>https://datasheets.raspberrypi.com/bcm2836/bcm2836-peripherals.pdf

# Depuración
1) En la aplicación de interfaz de usuario, añadiremos un led asignado al GPIO 5 y otro al GPIO 6, un botón para el GPIO 19 y otro para el 20, y ejecutamos la opción de depuración.

2) Para poder observar el comportamiento del programa, podremos simplemente hacer un breakpoint en el main. Al ser de espera activa, el programa estará constantemente verificando si alguno de los dos botones
ha sido pulsado, y dependiendo del botón, se realizará el comportamiento correspondiente explicado previamente.
