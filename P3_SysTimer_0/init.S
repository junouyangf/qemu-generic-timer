 			.global start

			@ -- Constantes
			.equ SVCStack,	 0x8000
			.equ IRQStack,	 0x4000

			.text
start:		@ -- Tabla de vectores de excepción
    		ldr pc,reset_handler
    		ldr pc,undefined_handler
    		ldr pc,svc_handler
    		ldr pc,prefetch_handler
    		ldr pc,data_handler
    		ldr pc,unused_handler
    		ldr pc,irq_handler
    		ldr pc,fiq_handler

			@ -- Direcciones de las rutinas de tratamiento
reset_handler:		.word reset
undefined_handler:	.word hang
svc_handler:		.word hang
prefetch_handler:	.word hang
data_handler:		.word hang
unused_handler:		.word hang
irq_handler:		.word isr_irq
fiq_handler:		.word hang

reset:		@ -- Rutina de tratamiento de reset (no retorna)

    		ldr r0,=start
    		mov r1,#0x0000
    		ldr r2,=reset
	        @@@ Copiar código de _start a la 0x0000
L0:			cmp r0, r2
			beq InitStacks
			ldr r3, [r0], #4
			str r3, [r1], #4
			b L0
			
InitStacks: @ Inicialización de los Stacks

    		@ Modificar estado (IRQ_MODE|FIQ_DIS|IRQ_DIS)
    		mov r0,#0xD2 
    		msr cpsr_c,r0
    		ldr sp, =IRQStack

			@ Modificar estado (SVC_MODE|FIQ_DIS|IRQ_DIS)
			mov r0,#0xD3
			msr cpsr_c,r0
			ldr sp, =SVCStack
            	
			@ Inicialización del Frame Pointer
    		mov fp,#0

			@ Salto a la función main()
    		bl main
			
			@ Bucle infinito
hang: 		b hang

			.globl enable_irq

enable_irq:
    		@@@ Habilitar la línea IRQ en el CPSR 
			mrs r0, cpsr
			bic r0, r0, #(1<< 7)
			msr cpsr_c, r0
			bx lr
			
.globl PUT32
PUT32:
    str r1,[r0]
    bx lr

.globl GET32
GET32:
    ldr r0,[r0]
    bx lr
    
.end
