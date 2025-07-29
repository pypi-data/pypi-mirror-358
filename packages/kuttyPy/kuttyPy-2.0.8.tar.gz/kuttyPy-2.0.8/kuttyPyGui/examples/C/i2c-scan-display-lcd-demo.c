/*
Scan the I2C bus and send via UART. also display results on an I2C LCD screen.
*/

#include <avr/kp.h>   // Include file for I/O operations



int main (void)
{

uint8_t addresses[20], found,temp_cmd[]={0xF4, 0x2E}, res[10]={0,0,0,0,0,0,0,0,0,0},i=0;

i2c_init();
i2c_lcd_init();
uart_init(38400);


for(;;)
    {

	found = i2c_scan(&addresses[0]);

	for(i=0;i<found;i++){	
		uart_send_byte_ascii(addresses[i]);
		uart_send_byte(',');

		//BMP180 detected at 119 (0x77). read values from it and send over UART
		for(;addresses[i] == 0x77;){
				delay_ms(10);
				i2c_write(0x77 , &temp_cmd[0], 2);
				delay_ms(10);
				i2c_read(0x77, 0xF6, &res[0],2);
				uart_send_byte_ascii(res[0]);
				uart_send_byte(',');
				uart_send_byte_ascii(res[1]);
				uart_send_byte('\n');
			}

		

		}
	if(found)
		uart_send_byte('\n');
          delay_ms(500);



  }

return 0;
}