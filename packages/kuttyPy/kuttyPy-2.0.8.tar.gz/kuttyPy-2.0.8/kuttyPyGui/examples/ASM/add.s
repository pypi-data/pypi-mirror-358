; program add.s (does not use the pre-processor)

ddrb = 0x17
portb = 0x18

.section .text    ; denotes code section
.global main
main:  

     LDI  R16, 255        ; load R16 with 255
     OUT  ddrb, R16
     LDI  R16,  251       ;  load R16 with 2
     LDI  R17,  3         ;  load R17 with 4
     ADD  R16, R17        ;  R16 <- R16 + R17
     OUT  portb, R16      ; result to port B
.END
