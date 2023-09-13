#include "bcm2837.h"

#define LED_OFF 0
#define LED_ON  1
#define BUTTON_PUSHED   1
#define BUTTON_RELEASED 0

#define CS  0x3F003000
#define CLO 0x3F003004
#define C0  0x3F00300C
#define C1  0x3F003010
#define C2  0x3F003014
#define C3  0x3F003018

extern void enable_irq();
extern void PUT32 ( unsigned int, unsigned int );
extern unsigned int GET32 ( unsigned int );

void c_irq_handler(void) __attribute__ ((interrupt ("IRQ")));
int mode = 0;
int led;
int led2;
unsigned int interval=0x00800000;
volatile unsigned int irq_counter;

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




void setup_gpio()
{
    	// Configurar GPIO 19 como INPUT
	GPFSEL1 = GPFSEL1 & ~(0x7 << 9*3);

	
	// Configurar GPIO 6 como OUTPUT
	GPFSEL0 = (GPFSEL0 & ~(0x7 << 6*3)) | (0x1 << 6*3);

	
	// Activar detección de flanco de subida para GPIO 19
	GPREN0 = (0x1 << 19);

	// Habilitar las interrupciones gpio_int[0]
	IRQ_ENABLE_IRQS_2 = (0x1 << 17);
	
	enable_irq();
}


void c_irq_handler (void)
{
	
	if(GET32(CS) & 0x2){	
		
		unsigned int rx=GET32(CLO);
			
		rx+=interval;
			
		PUT32(C1,rx);

		led2_switch();
		
		PUT32(CS, 2);
	}
	else if (IRQ_PEND2 & (0x1 << 17)) {
		//Interrupción del GPIO19
		if (GPEDS0 & (0x1 << 19)) {
			if (button_read() == BUTTON_PUSHED) {
				//Tratamos la pulsación del botón
				
				mode = (mode+ 1)%2;
				if (mode == 0)interval=0x00800000;
				else interval=0x0080000;
				unsigned int rx=GET32(CLO);
			
				rx+=interval;
					
				PUT32(C1,rx);

				led2_switch();
				
				PUT32(CS, 2);
			}
			//Reconocemos la interrupción
			GPEDS0 = 0x1 << 19;
		}
	}
}


// El System Timer nos proporciona 4 canales de temporizadores y un free-running counter. 
// Funcionamiento: Cada uno de estos canales posee un registro COMPARE cuyo valor comparamos con
// los 32 bits menos significativos del valor del free-running counter. Por tanto, cuando uno de
// los valores de estos registros coincide con valor del contador, se genera una señarl de interrupción.
int main (void)
{

	
	unsigned int rx;

	setup_gpio();

	led_off();
	led2_off();

	// CLO nos devuelve los últimos 32 bits del free-running counter.
	rx=GET32(CLO);
	rx+=interval;
	
	// Almacenamos el valor el registro COMPARE 1. Cuando el free-running counter coincida con
	// este valor se producirá la interrupción.
	// Escribimos un 1 en el bit 1 del CS para limpiar el estado de comparación.
	PUT32(C1,rx);
	PUT32(CS,2);
	
	// IRQ_ENBALE_IRQS1
	PUT32(0x3F00B210,0x00000002);
	while(1);
	
	
	return 0;
}

