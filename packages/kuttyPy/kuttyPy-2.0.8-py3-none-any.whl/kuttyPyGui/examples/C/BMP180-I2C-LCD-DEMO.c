/*
Scan the I2C bus and send via UART. also display results on an I2C LCD screen.
*/

#include "./kplib/kp.h"   // Include file for I/O operations



int main (void)
{

uint8_t addresses[20], found,temp_cmd[]={0xF4, 0x2E}, res[10]={0,0,0,0,0,0,0,0,0,0},i=0,bmp_found=0;
char a[10];
i2c_init();
i2c_lcd_init();

for(;;)
    {

	if(bmp_found){ //read raw values from it and show
		i2c_write(0x77 , &temp_cmd[0], 2);
		delay_ms(10);
		i2c_read(0x77, 0xF6, &res[0],2);


		i2c_lcd_put_string("BMP180: ",2); // set row 2
		utoa(res[0], a, 10);//convert to ascii string
		i2c_lcd_put_string(a,0); // do not set row. append

		i2c_lcd_put_string(",",0); // do not set row. append

		utoa(res[1], a, 10);//convert to ascii string
		i2c_lcd_put_string(a,0); // do not set row. append

		}
	else{
	// scan the I2C bus. found=number of sensors found. 
	found = i2c_scan(&addresses[0]);
	i2c_lcd_clear(); // clear the screen
	i2c_lcd_put_string("I2C: ",1); // set row  1
	bmp_found = 0;
	//iterate through addresses

	for(i=0;i<found;i++){
		utoa(addresses[i], a, 10);//convert to ascii string
		i2c_lcd_put_string(a,0); // do not set row. it will append to I2C: 
		i2c_lcd_put_string("/",0); 

		//BMP180 detected at 119 (0x77). 
		if(addresses[i] == 0x77)
			bmp_found = 1;

		}
	}

	delay_ms(100);

  }

return 0;
}