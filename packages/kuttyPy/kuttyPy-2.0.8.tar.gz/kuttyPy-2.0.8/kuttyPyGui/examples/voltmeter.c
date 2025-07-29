#include <avr/kp.h>   // Include file for I/O operations

int main (void)
{
uint16_t data;
float v;

DDRB = 255;             // Configure port B as output  
adc_enable();
lcd_init();

while (1)
    {
     data = read_adc(0);
     v = data * 5.0 / 1023; 
     PORTB = data >> 2;    // convert 10 bit in to 8 bit
     lcd_clear();
     lcd_put_float(v, 3);   // 3 decimals
     delay_ms(500);
    }
}
