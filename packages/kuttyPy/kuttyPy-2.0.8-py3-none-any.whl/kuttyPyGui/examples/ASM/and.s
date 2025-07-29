; program add.s (does not use the pre-processor)

ddrb = 0x17       ; I/O mapped addresses 
portb = 0x18
ddrd = 0x11 
portd = 0x12 
SREG = 0x5F       ; memory mapped address of status register

.section .text    ; denotes code section
.global main
main:  

     LDI  R16, 255        ; load R16 with 255
     OUT  ddrb, R16
     OUT  ddrd, R16
     ANDI  R16, 1         ;  result in R16
     OUT  portb, R16      ;  result to port B
     LDS  R17, SREG
     OUT  portd, R17      ;  status to port D
.END
