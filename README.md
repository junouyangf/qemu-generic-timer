Raspberry Pi 3b bare metal.

|nombre          |                                                           |
|----------------|-----------------------------------------------------------|
|[P3_INTA_3b](https://github.com/junouyangf/qemu-int/tree/main/P3_INTA_3b)|Práctica 3 implementada con ARM Timer (no funcional)|
|[P3_INTP_3b](https://github.com/junouyangf/qemu-int/tree/main/P3_INTP_3b)|Práctica 3 implementada con Generic Timer|
|[P3_INTS_3b](https://github.com/junouyangf/qemu-int/tree/main/P3_INTS_3b)|Práctica 3 implementada con System Timer (para la raspi0)|
|[P3_INTS_3b](https://github.com/junouyangf/qemu-int/tree/main/P3_INTS_3b)|Práctica 3 implementada con System Timer|
|[P3_INT_3b](https://github.com/junouyangf/qemu-int/tree/main/P3_INT_3b)|Práctica 3 implementada con Interrupciones GPIO (sin timer)|

# Toolchain
Toolchain usado para la compilación del código para la raspi 3b. (gcc-system-aarch64)
>https://developer.arm.com/downloads/-/gnu-a

# Qemu 7.0.0
Versión empleada: 7.0.0
>https://download.qemu.org/

Parche aplicado para la generación de interrupciones mediante los GPIOs
>https://github.com/berdav/qemu/commit/494087f249ec1c0d7c5d19818129245aa9338aab
