#include <avr/io.h>   // Include file for I/O operations

int main (void)
{
DDRA = 0;               // Port A as Input
PORTA = 255;            // Enable pullups
DDRB = 255;             // Configure port B as output  

while (1)
    {
     PORTB = PINA;
    }
}
