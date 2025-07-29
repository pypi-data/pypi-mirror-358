/*
Read A6 and A7 ADC values and display results on an I2C LCD screen.
connect joystick such that A6, A7 are connected to X and Y. 5V and GND are adjacent.
*/

#include <avr/kp.h>   // Include file for I/O operations



int main (void)
{

char a[10];
i2c_init();
i2c_lcd_init();

adc_enable();

i2c_lcd_clear(); // clear the screen
i2c_lcd_put_string("ADC A6,A7: ",1); // set row 1

for(;;)
    {
	utoa(read_adc(6), a, 10);//convert to ascii string
	i2c_lcd_put_string(a,2); // row 2
	i2c_lcd_put_string(",",0);
	utoa(read_adc(7), a, 10);//convert to ascii string
	i2c_lcd_put_string(a,0); // do not set row. append
	i2c_lcd_put_string("    ",0);// clear remaining space

	delay_ms(500);

  }

return 0;
}