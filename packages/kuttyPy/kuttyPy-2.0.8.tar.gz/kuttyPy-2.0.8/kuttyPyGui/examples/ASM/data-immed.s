
ddrb  = 0x17          ; I/O mapped address of DDRB
portb = 0x18         ; and PORTB

         .section .text    ; denotes code section
         .global main
main: 	
  LDI R16, 255       ; load R16 with 255
  OUT ddrb, R16      ; Display content of R16
  OUT portb, R16     ; using LEDs on port B
.end
