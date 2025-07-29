
#include <avr/kp.h>   // Include file for I/O operations



int main (void)
{
i2c_lcd_init();

i2c_lcd_clear();
i2c_lcd_put_string("row  one!",1);
i2c_lcd_put_string("row  two!",2);

}
