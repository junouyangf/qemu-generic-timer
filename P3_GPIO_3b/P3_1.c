#include "bcm2837.h"

#define LED_OFF 0
#define LED_ON  1
#define BUTTON_PUSHED   1
#define BUTTON_RELEASED 0

extern void enable_irq();

void c_irq_handler(void) __attribute__ ((interrupt ("IRQ")));

int led;


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


void led_switch(void)
{
    if (led == LED_OFF)
        led_on();
    else
        led_off();
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
	
	// Activar detección de flanco de subida para GPIO 19
	GPREN0 = (0x1 << 19);

	// Habilitar las interrupciones gpio_int[0-3]
	// Los IRQ de los GPIO corresponden a los bits 17,18,19 y 20 de IRQ_ENABLE2
	IRQ_ENABLE_IRQS_2 = (0x1 << 17);
	
	// Habilitar las irq en el cpsr (codigo ensamblador)
	enable_irq();	
}


void c_irq_handler (void)
{
	// Comprobar si hay alguna petición pendiente
	if (IRQ_BASIC & (0x1 << 9)) {
		// Interrupción gpio_int[3] pendiente
		// Los GPIOS del 0 al 31 corresponden al bit 17.
		if (IRQ_PEND2 & (0x1 << 17)) {
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
}


int main (void)
{

	setup_gpio();
	
	led_off();
	
	while (1);
	
	return 0;
}


