//#include <avr/io.h>
//#include <inttypes.h>

//#include <avr/kp.h>
#include <avr/io.h>
#include <util/twi.h>

#include "kp.h"

uint32_t delay_countdown=0;


/*************************************************************************
 Initialization of the I2C bus interface. Need to be called only once
*************************************************************************/
void i2c_init(void)
{
TWSR=0x00; TWBR=0x46 ; TWCR=0x04; //Init I2C
PORTC |= 3; //Enable SCL/SDA Pull up	
}/* i2c_init */


/*************************************************************************
Scan I2C Bus
*data : First Location of the array of bytes to fill with addresses

returns: total addresses found.
*************************************************************************/

uint8_t i2c_scan(uint8_t *data)
{
	uint8_t found=0;
	uint16_t timeout=11000;

	DDRC |= 1  ;// SCL as output .
	PORTC &= ~3; while(timeout--); PORTC |=3; //Pull SCL low. some sensors need this.
	DDRC &= ~3 ;// SCL as input
	PORTC |= 3; //Enable SCL/SDA Pull up	
	timeout=50000;

	for(uint8_t i = 1;i <= 127;i++){
		TWCR = 0xA4;             // send a start bit on i2c bus
		while(!(TWCR & 0x80) && timeout)timeout--;                  // wait for confirmation of transmit
		TWDR = i<<1;          // load address of i2c device
		TWCR = 0x84;             // transmit
		while(!(TWCR & 0x80) && timeout)timeout--;                  // wait for confirmation of transmit
		asm("WDR");
		if((TWSR&0xFC) == 0x18){   // SLA+W has been transmitted; ACK has been received
			*(data++) = i;
			found++;
		}		
		TWCR = 0x94;             // stop bit
	}
	return found;
}



/*************************************************************************
Write data over I2C
address  : value from 0 to 127
*data : First Location of the array of bytes to write
numbytes : Number pf bytes to write

returns: 0 if timeout, 1 if successful.
*************************************************************************/

uint8_t i2c_write(uint8_t address, uint8_t *data, uint8_t numbytes)
{

	uint16_t timeout = 10000;
	TWCR = 0xA4;                                                // send a start bit on i2c bus
	while(!(TWCR & 0x80) && timeout)timeout--;                  // wait for confirmation of transmit
	TWDR = address<<1;                                             // load address of i2c device
	TWCR = 0x84;                                                // transmit
	while(!(TWCR & 0x80) && timeout)timeout--;                  // wait for confirmation of transmit

	while(numbytes--){			//
		TWDR = *(data++);
		TWCR = 0x84;                                                // transmit
		while(!(TWCR & 0x80) && timeout)timeout--;                  // wait for confirmation of transmit
		asm("WDR");
	}
	TWCR = 0x94;                                                // stop bit
	if(timeout)return 0;		                                    // send timeout status
	else return 1;
}


/*************************************************************************
Read data from I2C
address  : value from 0 to 127
reg : value of the register(In I2C client device) to read from 
*data : First Location of the array of bytes to fill with read data
numbytes : Number of bytes to read

returns: 0 if timeout, 1 if successful.
*************************************************************************/

uint8_t i2c_read(uint8_t address, uint8_t reg, uint8_t *data, uint8_t numbytes)
{
	uint16_t timeout = 10000;
	TWCR = 0xA4;                                   // send a start bit on i2c bus
	while(!(TWCR & 0x80) && timeout)timeout--;    // wait for confirmation of transmit
	TWDR = address<<1;                                // load address of i2c device
	TWCR = 0x84;                                                // transmit
	while(!(TWCR & 0x80) && timeout)timeout--;      // wait for confirmation of transmit

	TWDR = reg;		              // write the register to read from.
	TWCR = 0x84;                       // transmit
	while(!(TWCR & 0x80) && timeout)timeout--;                  // wait for confirmation of transmit
	asm("WDR");

	TWCR = 0xA4;                                                // send a repeated start bit on i2c bus
	while(!(TWCR & 0x80) && timeout)timeout--;                  // wait for confirmation of transmit
	TWDR = address<<1|1;                                           // load address of i2c device [ READ MODE ]
	TWCR = 0xC4;                                                // transmit
	while(!(TWCR & 0x80) && timeout)timeout--;                  // wait for confirmation of transmit

	while(numbytes > 1){
		TWCR = 0xC4;                                 // transmit, ACK (byte request)
		while(!(TWCR & 0x80) && timeout)timeout--;    // wait for confirmation of transmit
		
		*(data++) = TWDR;		            // and grab the target data
		asm("WDR");
		numbytes --;
	}
	TWCR = 0x84;                    	         // transmit, NACK (last byte request)
	while(!(TWCR & 0x80) && timeout)timeout--;       // wait for confirmation of transmit
	*(data++) = TWDR;         		          // and grab the target data
	TWCR = 0x94;                          	         // stop bit

	if(timeout)return 0;		        // send timeout status
	else return 1;
}








unsigned char I2CStart() {
	/* Send START condition */
	TWCR =  (1 << TWINT) | (1 << TWEN) | (1 << TWSTA);
	
	/* Wait for TWINT flag to set */
	while (!(TWCR & (1 << TWINT)));
	
	/* Check error */
	if (TW_STATUS != TW_START && TW_STATUS != TW_REP_START)
	{
		return TW_STATUS;
	}
	

	return SUCCESS;
}

void I2CStop() {
	TWCR = 0x94;             // stop bit
}



void I2CWait() {
    delay_countdown=1000;
    /* Wait for TWINT flag to set */
	while (!(TWCR & (1 << TWINT)) && delay_countdown--)delay_us(1);	
    /* wait for any pending transfer */
}

unsigned char I2CSend(unsigned char dat) {
    delay_countdown=1000;

	/* Transmit 1 byte*/

	TWDR = dat;
	TWCR = (1 << TWINT) | (1 << TWEN);
	
	/* Wait for TWINT flag to set */
	while (!(TWCR & (1 << TWINT)));
	if (TW_STATUS != TW_MT_DATA_ACK)
	{

		return TW_STATUS;
	}
	

	return SUCCESS;

    I2CWait(); /* wait for any pending transfer */
}





/*

int main (void)
  {

uint8_t addresses[20], found, temp_cmd[]={0xF4, 0x2E}, res[10]={0,0,0,0,0,0,0,0,0,0};

i2c_init();
uart_init(38400);

DDRB=255;
for(;;)
    {
	PORTB = 0;
	delay_ms(10);
	found = i2c_scan(&addresses[0]);
	if(found){	
		PORTB = addresses[0];
		uart_send_byte_ascii(addresses[0]);
		for(;addresses[0] == 0x77;){
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
          delay_ms(100);
  }

return 0;
}

*/
