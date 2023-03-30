#include "bcm2837.h"
#include <stddef.h>
#include <stdint.h>

#define LED_OFF 0
#define LED_ON  1
#define BUTTON_PUSHED   1
#define BUTTON_RELEASED 0
#define TRACKING 1
#define INVERSE 0

extern void enable_irq();

void c_irq_handler(void) __attribute__ ((interrupt ("IRQ")));

int led;
int led2;


void led_on(void)
{
    GPSET0 = 0x1 << 5;
    led = LED_ON;
}


void led_off(void)
{
    GPCLR0 = 0x1 << 5;
    led    = LED_OFF;
}


void led2_on(void)
{
    GPSET0 = 0x1 << 6;
    led2 = LED_ON;
}


void led2_off(void)
{
    GPCLR0 = 0x1 << 6;
    led2    = LED_OFF;
}


void led_switch(void)
{
    if (led == LED_OFF)
        led_on();
    else
        led_off();
}


void led2_switch(void)
{
    if (led2 == LED_OFF)
        led2_on();
    else
        led2_off();
}


int button_read(void)
{
    int button = BUTTON_RELEASED;

    if ((GPLEV0 & (0x1 << 19)))
        button = BUTTON_PUSHED;

    return button;
}


void short_wait(void)
{
	int w;
	for (w=0; w<100; w++) {
		w++;
		w--;
	}
}


void long_wait(void)
{
	int w;
	for (w=0; w<100; w++) {
		short_wait();
	}
}


void setup_gpio()
{
    	// Configurar GPIO 19 como INPUT (000) --> Boton
	GPFSEL1 = GPFSEL1 & ~(0x7 << 9*3);
	
	// Configurar GPIO 5 como OUTPUT (001) --> LED
	GPFSEL0 = (GPFSEL0 & ~(0x7 << 5*3)) | (0x1 << 5*3);
	
	// Configurar GPIO 6 como OUTPUT (001) --> LED2
	GPFSEL0 = (GPFSEL0 & ~(0x7 << 6*3)) | (0x1 << 6*3);
	
	// Activar el pull-up del GPIO 19
	GPPUD = 0x2;
	short_wait();
	GPPUDCLK0 = (0x1 << 19);
	short_wait();
	GPPUD = 0;
	GPPUDCLK0 = 0;
	
	// Activar detección de flanco de subida para GPIO 19
	GPREN0 = (0x1 << 19);
	
	// Habilitar las interrupciones gpio_int[0-3]
	// Los IRQ de los GPIO corresponden a los bits 17,18,19 y 20 de IRQ_ENABLE2
	IRQ_ENABLE_IRQS_2 = (0x1 << 17);

	// Habilitar las irq en el cpsr (codigo ensamblador)
	enable_irq();
	
	// Setup del timer
	ARM_TIMER_LOD = 500000; // N
	ARM_TIMER_DIV = 999; // D
	ARM_TIMER_CLI = 0;
	
	// Pre-escalado 1, contador de 32 bits, habilitamos timer e interrupciones
	ARM_TIMER_CTL = ARM_TIMER_ENABLE | ARM_TIMER_IRQ_ENABLE | ARM_TIMER_23b;
	
	// Habilitar las interrupciones del timer
	IRQ_ENABLE_BASIC = 0x1;
}


void c_irq_handler (void)
{
	// Comprobar si hay alguna petición pendiente
	if (IRQ_BASIC & 0x1) {
		// Interrupcion del timer
		led2_switch();
		// Reconocemos la interrupcion
		ARM_TIMER_CLI = 0x1;
	}		
	else if (IRQ_PEND2 & (0x1 << 17)) {
		//Interrupción del GPIO19
		if (GPEDS0 & (0x1 << 19)) {
			long_wait();
			if (button_read() == BUTTON_PUSHED) {
				//Tratamos la pulsación del botón
				led_switch();
			}
			//Reconocemos la interrupción
			GPEDS0 = 0x1 << 19;
		}
	}
}


int main (void)
{

	setup_gpio();
	
	led_off();
	
	led2_off();
	
	while (1);
	
	return 0;
}


