#include "bcm2837.h"

#define LED_OFF 0
#define LED_ON  1
#define BUTTON_PUSHED   1
#define BUTTON_RELEASED 0

int led1, led2;

void led1_on(void)
{
    GPSET0 = 0x1 << 5;
    led1 = LED_ON;
}

void led1_off(void)
{
    GPCLR0 = 0x1 << 5;
    led1    = LED_OFF;
}

void led1_switch(void)
{
    if (led1 == LED_OFF)
        led1_on();
    else
        led1_off();
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

void led2_switch(void)
{
    if (led2 == LED_OFF)
        led2_on();
    else
        led2_off();
}

int button1_read(void)
{
    int button = BUTTON_RELEASED;

    if ((GPLEV0 & (0x1 << 19)))
        button = BUTTON_PUSHED;

    return button;
}

int button2_read(void)
{
    int button = BUTTON_RELEASED;

    if ((GPLEV0 & (0x1 << 20)))
        button = BUTTON_PUSHED;

    return button;
}





void setup_gpio()
{
    // Configuramos GPIO 5 como OUTPUT 
    GPFSEL0 = (GPFSEL0 & ~(0x7 << 5*3)) | (0x1 << 5*3);

    // Configuramos GPIO 6 como OUTPUT
    GPFSEL0 = (GPFSEL0 & ~(0x7 << 6*3)) | (0x1 << 6*3);

    // Configuramos GPIO 19 como INPUT 
    GPFSEL1 = GPFSEL1 & ~(0x7 << 9*3);

    // Configuramos GPIO 20 como INPUT
    GPFSEL2 = GPFSEL2 & ~(0x7 << 0*3);

}

int main (void)
{
    int P1_st, P2_st;
    setup_gpio();

    //Inicializar L1 y L2 a apagado
    led1_off();
    led2_off();

	while (1) {
		// Esperar a que se pulse P1 o P2
		do {
			P1_st = button1_read();
			P2_st = button2_read();
		} while ((P1_st == BUTTON_RELEASED) && (P2_st == BUTTON_RELEASED));

		if (P1_st == BUTTON_PUSHED) {

			led1_switch();
			led2_switch();

			while (button1_read() != BUTTON_RELEASED);
		}

		if (P2_st == BUTTON_PUSHED) {
			led2_switch();
			while (button2_read() != BUTTON_RELEASED);
		}
	}

    return 0;
}
