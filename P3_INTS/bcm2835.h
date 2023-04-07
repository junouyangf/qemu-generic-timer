// Registros mini UART (pp. 8 BCM2835 ARM Peripherals y Manual 16550D)
#define AUX_IRQ			(*(volatile unsigned *)0x20215000)
#define AUX_ENABLES     (*(volatile unsigned *)0x20215004)
#define AUX_MU_IO_REG   (*(volatile unsigned *)0x20215040)
#define AUX_MU_IER_REG  (*(volatile unsigned *)0x20215044)
#define AUX_MU_IIR_REG  (*(volatile unsigned *)0x20215048)
#define AUX_MU_LCR_REG  (*(volatile unsigned *)0x2021504C)
#define AUX_MU_MCR_REG  (*(volatile unsigned *)0x20215050)
#define AUX_MU_LSR_REG  (*(volatile unsigned *)0x20215054)
#define AUX_MU_MSR_REG  (*(volatile unsigned *)0x20215058)
#define AUX_MU_SCRATCH  (*(volatile unsigned *)0x2021505C)
#define AUX_MU_CNTL_REG (*(volatile unsigned *)0x20215060)
#define AUX_MU_STAT_REG (*(volatile unsigned *)0x20215064)
#define AUX_MU_BAUD_REG (*(volatile unsigned *)0x20215068)

// Macros para la gestión de la uart
#define AUX_MU_IIR_RXINT ((AUX_MU_IIR_REG & (0x3 << 1)) == (0x2 << 1))
#define AUX_MU_IIR_TXINT ((AUX_MU_IIR_REG & (0x3 << 1)) == (0x1 << 1))

// Registros ARM Timer (pp. 196 BCM2835 ARM Peripherals y Manual SP804)
#define ARM_TIMER_LOD 	(*(volatile unsigned *)0x2000B400)
#define ARM_TIMER_VAL 	(*(volatile unsigned *)0x2000B404)
#define ARM_TIMER_CTL 	(*(volatile unsigned *)0x2000B408)
#define ARM_TIMER_CLI 	(*(volatile unsigned *)0x2000B40C)
#define ARM_TIMER_RIS 	(*(volatile unsigned *)0x2000B410)
#define ARM_TIMER_MIS 	(*(volatile unsigned *)0x2000B414)
#define ARM_TIMER_RLD 	(*(volatile unsigned *)0x2000B418)
#define ARM_TIMER_DIV 	(*(volatile unsigned *)0x2000B41C)
#define ARM_TIMER_CNT 	(*(volatile unsigned *)0x2000B420)

// Macros para gestión ARM Timer (pp. 196 BCM2835 ARM Peripherals y Manual SP804)
#define ARM_TIMER_COUNT_PRES(v)	((v)<<16)
#define ARM_TIMER_ENABLE		(1<<7)
#define ARM_TIMER_IRQ_ENABLE	(1<<5)
#define ARM_TIMER_23b			(1<<1)


// Registros SPI
#define SPI_CS 			(*(volatile unsigned *)0x20204000)
#define SPI_FIFO 		(*(volatile unsigned *)0x20204004)
#define SPI_CLK 		(*(volatile unsigned *)0x20204008)

// Macros SPI
	// Campos del registro SPI CS
#define SPI_CS_LEN_LONG		(1 << 25)
#define SPI_CS_DMA_LEN		(1 << 24)
#define SPI_CS_CSPOL2		(1 << 23)
#define SPI_CS_CSPOL1		(1 << 22)
#define SPI_CS_CSPOL0		(1 << 21)
#define SPI_CS_RX			(1 << 20)
#define SPI_CS_RXR			(1 << 19)
#define SPI_CS_TXD			(1 << 18)
#define SPI_CS_RXD			(1 << 17)
#define SPI_CS_DONE			(1 << 16)
#define SPI_CS_LEN			(1 << 13)
#define SPI_CS_REN			(1 << 12)
#define SPI_CS_ADCS			(1 << 11)
#define SPI_CS_INTR			(1 << 10)
#define SPI_CS_INTD			(1 << 9 )
#define SPI_CS_DMAEN		(1 << 8 )
#define SPI_CS_TA		 	(1 << 7 )
#define SPI_CS_CSPOL		(1 << 6 )
#define SPI_CS_CLEAR_RX		(1 << 5 )
#define SPI_CS_CLEAR_TX		(1 << 4 )
#define SPI_CS_CPOL			(1 << 3 )
#define SPI_CS_CPHA			(1 << 2 )
#define SPI_CS_CS1		 	(1 << 1 )
#define SPI_CS_CS0			(1 << 0 )



// Registros System Timer (pp. 172 BCM2835 ARM Peripherals)
#define SYSTIMERCLO 	(*(volatile unsigned *)0x20003004)

// Registros GPIO (pp. 89 BCM2835 ARM Peripherals)
#define GPFSEL0 		(*(volatile unsigned *)0x20200000)
#define GPFSEL1 		(*(volatile unsigned *)0x20200004)
#define GPFSEL2 		(*(volatile unsigned *)0x20200008)
#define GPSET0  		(*(volatile unsigned *)0x2020001C)
#define GPCLR0  		(*(volatile unsigned *)0x20200028)
#define GPLEV0			(*(volatile unsigned *)0x20200034)
#define GPEDS0			(*(volatile unsigned *)0x20200040)

#define GPREN0			(*(volatile unsigned *)0x2020004C)
#define GPFEN0			(*(volatile unsigned *)0x20200058)
#define GPHEN0			(*(volatile unsigned *)0x20200064)
#define GPLEN0			(*(volatile unsigned *)0x20200070)
#define GPAREN0			(*(volatile unsigned *)0x2020007C)
#define GPAFEN0 		(*(volatile unsigned *)0x20200088)
#define GPPUD    		(*(volatile unsigned *)0x20200094)
#define GPPUDCLK0       (*(volatile unsigned *)0x20200098)
#define GPLEV0          (*(volatile unsigned *)0x20200034)

// Macros para gestión de GPIOs (pp. 89 BCM2835 ARM Peripherals)
#define GPIO_IN         0x0
#define GPIO_OUT        0x1
#define GPIO_ALT0       0x4
#define GPIO_ALT1       0x5
#define GPIO_ALT2       0x6
#define GPIO_ALT3       0x7
#define GPIO_ALT4       0x3
#define GPIO_ALT5       0x2		

#define FSEL23          9
#define FSEL18          24
#define FSEL17          21
#define FSEL15          15
#define FSEL14          12
#define FSEL7           21
#define FSEL8 			24
#define FSEL9			27
#define FSEL10			0
#define FSEL11 			3
#define FSEL12			6

// Registros para gestión interrupciones (pp. 112 BCM2835 ARM Peripherals)
#define IRQ_BASIC 			(*(volatile unsigned *)0x2000B200)
#define IRQ_PEND1 			(*(volatile unsigned *)0x2000B204)
#define IRQ_PEND2 			(*(volatile unsigned *)0x2000B208)
#define IRQ_ENABLE_IRQS_1	(*(volatile unsigned *)0x2000B210)
#define IRQ_ENABLE_IRQS_2	(*(volatile unsigned *)0x2000B214)
#define IRQ_ENABLE_BASIC 	(*(volatile unsigned *)0x2000B218)
#define IRQ_DISABLE_IRQS_1	(*(volatile unsigned *)0x2000B21C)
#define IRQ_DISABLE_IRQS_2	(*(volatile unsigned *)0x2000B220)
#define IRQ_DISABLE_BASIC 	(*(volatile unsigned *)0x2000B224)

// Macros para gestión interrupciones (pp. 112 BCM2835 ARM Peripherals)
#define GPIO_INT		17
#define AUX_INT			29
#define IRQ_TIMER       1
