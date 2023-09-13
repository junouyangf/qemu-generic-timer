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







void setup_gpio()
{
    	
	GPFSEL1 = GPFSEL1 & ~(0x7 << 9*3);
	
	
	GPFSEL0 = (GPFSEL0 & ~(0x7 << 5*3)) | (0x1 << 5*3);
	
	// Activar detección de flanco de subida para GPIO 19
	GPREN0 = (0x1 << 19);

	// Habilitar las interrupciones gpio_int[0]
	// Los IRQ de los GPIO corresponden a los bits 17,18,19 y 20 de IRQ_ENABLE2
	IRQ_ENABLE_IRQS_2 = (0x1 << 17);
	
	// Habilitar las irq 
	enable_irq();	
}


void c_irq_handler (void)
{
	
	if (IRQ_BASIC & (0x1 << 9)) {
		if (IRQ_PEND2 & (0x1 << 17)) {
			if (GPEDS0 & (0x1 << 19)) {
				if (button_read() == BUTTON_PUSHED) {
					
					led_switch();
				}
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


