.text
.globl _start
 
_start:

    mrs   x1, mpidr_el1
    and   x1, x1, #3
    cmp   x1, #0
    bne   hang 

    // direccion SP
    ldr   x1, =_start

    // bajar a EL2
    mov   x2, #0x401    // RW=1, NS=1
    msr   scr_el3, x2
    mov   x2, #0x3c9    // D=1, A=1, I=1, F=1 M=EL2h
    msr   spsr_el3, x2
    adr   x2, start_el2
    msr   elr_el3, x2
    eret

start_el2:
    // SP de EL1
    msr   sp_el1, x1
  
    mov   x0, #(1 << 31)      // AArch64
    
    msr   hcr_el2, x0

    // ponemos el vector de excepiciones a EL1
    ldr x0, =vector
    msr vbar_el1, x0 

    mov   x2, #0x3c4         // D=1, A=1, I=1, F=1 M=EL1t
    msr   spsr_el2, x2
    adr   x2, start_el1
    msr   elr_el2, x2
    eret

start_el1:
    // set sp
    mov   sp, #0x08000000

    bl main

hang:
    wfi
    b     hang

.globl enable_irq
enable_irq:
    msr   daifclr, #2
    ret

.globl disable_irq
disable_irq:
    msr   daifset, #2
    ret
    
.globl PUT32
PUT32:
    str x1,[x0]
    ret

.globl GET32
GET32:
    ldr x0,[x0]
    ret

irq:
    stp   x0,  x1,  [sp, #-16]!
    stp   x2,  x3,  [sp, #-16]!
    stp   x4,  x5,  [sp, #-16]!
    stp   x6,  x7,  [sp, #-16]!
    stp   x8,  x9,  [sp, #-16]!
    stp   x10, x11, [sp, #-16]!
    stp   x12, x13, [sp, #-16]!
    stp   x14, x15, [sp, #-16]!
    stp   x16, x17, [sp, #-16]!
    stp   x18, x19, [sp, #-16]!

    //bl    c_irq_handler

    ldp   x18, x19, [sp], #16
    ldp   x16, x17, [sp], #16
    ldp   x14, x15, [sp], #16
    ldp   x12, x13, [sp], #16
    ldp   x10, x11, [sp], #16
    ldp   x8,  x9,  [sp], #16
    ldp   x6,  x7,  [sp], #16
    ldp   x4,  x5,  [sp], #16
    ldp   x2,  x3,  [sp], #16
    ldp   x0,  x1,  [sp], #16
    eret

.balign 4096
vector:
.balign 128
    b hang
.balign 128
    b irq
.balign 128
    b hang
.balign 128
    b hang
.balign 128
    b hang
.balign 128
    b hang //
.balign 128
    b hang
.balign 128
    b hang
.balign 128
    b hang
.balign 128
    b hang //
.balign 128
    b hang
.balign 128
    b hang
.balign 128
    b hang
.balign 128
    b hang //
.balign 128
    b hang
.balign 128
