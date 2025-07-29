/*
Scan the I2C bus and send results via UART.
*/

#include <avr/kp.h>   // Include file for I/O operations


#define REG_CONTROL 0xF4
#define CMD_TEMP 0x2E

#define REG_RESULT 0xF6

int main (void)
{

uint8_t addresses[20], found,temp_cmd[]={REG_CONTROL, CMD_TEMP}, res[10]={0,0,0,0,0,0,0,0,0,0},i=0;

i2c_init();
uart_init(38400);


for(;;)
    {

	found = i2c_scan(&addresses[0]); // i2c scan will store the addresses in `addresses`, and return total found sensors.

	for(i=0;i<found;i++){	
		uart_send_byte_ascii(addresses[i]); // send address
		uart_send_byte(','); // send comma.

		//BMP180 detected at 119 (0x77). read values from it and send over UART
		for(;addresses[i] == 0x77;){
				delay_ms(10);
				// write to 0x77 (bmp180 address) , 0xF4 and 0x2E
				i2c_write(0x77 , &temp_cmd[0], 2); // init temperature measurement
				delay_ms(10);
				// read 2 bytes from the result register
				i2c_read(0x77, REG_RESULT, &res[0],2);

				uart_send_byte_ascii(res[0]); // send MSB
				uart_send_byte(',');
				uart_send_byte_ascii(res[1]); // send LSB
				uart_send_byte('\n');
				//  rawT = (res[0] << 8) + res[1]
			          //  a = c5 * (rawT  - c6)
                			// Temperature = a + (mc / (a + md))

				// sample values. loaded from the chip: 
				// c5 = 0.004824447631835938 
				// c6 = 20636.0 
				// mc = -942.88
				// md = 16.50625

			}

		

		}
	if(found)
		uart_send_byte('\n');
          delay_ms(500);

  }

return 0;
}