Raspberry Pi 3b bare metal.

|nombre          |                                                           |
|----------------|-----------------------------------------------------------|
|[GUI](https://github.com/junouyangf/qemu-int/tree/main/GUI)|Proyecto de Interfaz Gráfica|
|[esperaActiva](https://github.com/junouyangf/qemu-int/tree/main/P3_3b)|Programa bare-metal de E/S por espera activa|
|[intGpio](https://github.com/junouyangf/qemu-int/tree/main/P3_GPIO_3b)|Programa bare-metal implementado con Interrupciones GPIO (sin timer)|
|[intSysTimer](https://github.com/junouyangf/qemu-int/tree/main/P3_SysTimer_3b)|Programa bare-metal implementado con System Timer|

# Toolchain
Toolchain usado para la compilación del código para la raspi 3b. (gcc-system-aarch64)
>https://developer.arm.com/downloads/-/gnu-a

# Qemu 7.0.0
Versión empleada: 7.0.0
>https://download.qemu.org/

Parche aplicado para la generación de interrupciones mediante los GPIOs
>https://github.com/berdav/qemu/commit/494087f249ec1c0d7c5d19818129245aa9338aab
