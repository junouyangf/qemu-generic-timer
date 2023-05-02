#include "bcm2837.h"
#include <stddef.h>
#include <stdint.h>

#define LED_OFF 0
#define LED_ON  1
#define BUTTON_PUSHED   1
#define BUTTON_RELEASED 0
#define TRACKING 1
#define INVERSE 0

#define CORE0_TIMER_IRQCNTL 0x40000040
#define CORE0_IRQ_SOURCE    0x40000060

extern void enable_irq();

void c_irq_handler(void) __attribute__ ((interrupt ("IRQ")));
int mode = 0;
int led;
int led2;


// Memory-Mapped I/O output
static inline void mmio_write(intptr_t reg, uint32_t data)
{
    *(volatile uint32_t*) reg = data;
}

 
// Memory-Mapped I/O input
static inline uint32_t mmio_read(intptr_t reg)
{
    return *(volatile uint32_t*) reg;
}


static inline void io_halt(void)
{
    asm volatile ("wfi");
}


// CNTV = Virtual Timer
// Bit 3 de Core 0 Timer Interrupt Control = nCNTVIRQ IRQ control (0: IRQ disabled - 1: IRQ enabled)
void routing_core0cntv_to_core0irq(void)
{
    mmio_write(CORE0_TIMER_IRQCNTL, 0x08);
}


uint32_t read_core0timer_pending(void)
{
    uint32_t tmp;
    tmp = mmio_read(CORE0_IRQ_SOURCE);
    return tmp;
}


static uint32_t cntfrq = 0;


// CNTV_CTL_EL0 = Counter-timer Virtual Timer Control register
void enable_cntv(void)
{
    uint32_t cntv_ctl;
    cntv_ctl = 1;
	asm volatile ("msr cntv_ctl_el0, %0" :: "r" (cntv_ctl));
}


// CNTV_TVAL_EL0 = Counter-timer Virtual Timer Timer Value register
void write_cntv_tval(uint32_t val)
{
	asm volatile ("msr cntv_tval_el0, %0" :: "r" (val));
    return;
}


// CNTFRQ_EL0 = Counter-timer Frequency register
uint32_t read_cntfrq(void)
{
    uint32_t val;
	asm volatile ("mrs %0, cntfrq_el0" : "=r" (val));
    return val;
}


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
	

	// Configurar GPIO 6 como OUTPUT (001) --> LED2
	GPFSEL0 = (GPFSEL0 & ~(0x7 << 6*3)) | (0x1 << 6*3);
	
	
	// Activar detección de flanco de subida para GPIO 19
	GPREN0 = (0x1 << 19);

	// Habilitar las interrupciones gpio_int[0-3]
	// Los IRQ de los GPIO corresponden a los bits 17,18,19 y 20 de IRQ_ENABLE2
	IRQ_ENABLE_IRQS_2 = (0x1 << 17);
	
	cntfrq = read_cntfrq();
	
	// Clear cntv interrupt and set next 1 sec timer.
	write_cntv_tval(cntfrq);    
	
	// Habilitar las irq en el cpsr (codigo ensamblador)
	routing_core0cntv_to_core0irq();
    	enable_cntv(); 
	enable_irq();
}


void c_irq_handler (void)
{
	// Comprobar si hay alguna petición pendiente
	// Bit 3 de Core 0 Interrupt Source = CNTVIRQ Interrupt
	if (read_core0timer_pending() & (0x1 << 3)) {
		// Interrupcion del timer
		led2_switch();
		
		// Clear cntv interrupt and set next 1sec timer.
		write_cntv_tval(cntfrq);    
	}		
	else if (IRQ_PEND2 & (0x1 << 17)) {
		//Interrupción del GPIO19
		if (GPEDS0 & (0x1 << 19)) {
			long_wait();
			if (button_read() == BUTTON_PUSHED) {
				//Tratamos la pulsación del botón
				mode = (mode+ 1)%2;
				if(mode == 0)cntfrq = cntfrq/4;
				else cntfrq=cntfrq*4;
				led2_switch();
				// Clear cntv interrupt and set next 1sec timer.
				write_cntv_tval(cntfrq);
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


