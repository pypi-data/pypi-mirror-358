/*
Scan the I2C bus for TMAG5273 magnetometer. also display results on an I2C LCD screen.
*/

#include <avr/kp.h>
// Include file for I/O operations



int main (void)
{

uint8_t addresses[20], found,temp_cmd[]={0x12}, res[10]={0,0,0,0,0,0,0,0,0,0},i=0,mag_found=0;
char a[10];
i2c_init();
i2c_lcd_init();

for(;;)
    {




	if(mag_found){ //read raw values from it and show
		//i2c_write(68 , &temp_cmd[0], 1);
		//delay_ms(10);
		i2c_read(68, 0x12, &res[0],6);


		i2c_lcd_put_string("MAG_X: ",2); // set row 2
		itoa((int16_t)(((uint16_t)res[0] << 8) | (uint16_t)res[1]), a, 10);//convert to ascii string
		i2c_lcd_put_string(a,0); // do not set row. append

		}
	else{
		// scan the I2C bus. found=number of sensors found. 
		found = i2c_scan(&addresses[0]);
		i2c_lcd_clear(); // clear the screen
		i2c_lcd_put_string("ADDR: ",1); // set row  1
		//iterate through addresses
	
		for(i=0;i<found;i++){
			utoa(addresses[i], a, 10);//convert to ascii string
			i2c_lcd_put_string(a,0); // do not set row. it will append to I2C: 
			i2c_lcd_put_string("/",0); 
	
			//TMAG5273 detected at 68
			if(addresses[i] == 68){
				i2c_write(68 , (uint8_t[]){0,1}, 2);
				i2c_write(68 , (uint8_t[]){0x02,0x79}, 2);
				i2c_write(68 , (uint8_t[]){0x07,0x01}, 2);
				i2c_write(68 , (uint8_t[]){0x08,0xA4}, 2);
				i2c_write(68 , (uint8_t[]){0x01,0x22}, 2);
				mag_found = 1;
			}

		}
	}


	delay_ms(10);

  }

return 0;
}