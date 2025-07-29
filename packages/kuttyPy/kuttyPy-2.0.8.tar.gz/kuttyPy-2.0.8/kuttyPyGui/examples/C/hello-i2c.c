/*
*/

#include <avr/kp.h>   // Include file for I/O operations



int main (void)
{
i2c_init();
i2c_lcd_init();

i2c_lcd_put_string("HELLO",1);
return 0;
}