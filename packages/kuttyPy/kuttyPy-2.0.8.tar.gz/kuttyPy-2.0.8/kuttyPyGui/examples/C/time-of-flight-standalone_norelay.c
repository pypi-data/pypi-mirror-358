/* time of flight measurement of a falling object. 
 * An external electromagnet is used to drop a ball. Its driver pin is connected to B7.
 * The user now fixes this electromagnet at a fixed height from the floor/table, and attaches
 * a small steel ball to it. also connects the power to the electromagnet to B7.
 * (B7): The program waits for B7 level change.
 * Fall Detection Switch : 2 metal plates are used to make a switch connecting PA2 to GND.
 * When the ball falls, the plates will make contact, and PA2 will go LOW.

 * Author: jithinbp@gmail.com
 * License : gpl-v3
 * Date 28 May sept 2025

 */

#include <avr/kp.h>
#include <avr/interrupt.h>
#include <string.h>
#include <stdlib.h>

#define PIN_GREEN 0
#define GREEN_ON   PORTA |= (1<<PIN_GREEN)
#define GREEN_OFF  PORTA &= ~(1<<PIN_GREEN)

#define RED_ON   PORTB |= 127
#define RED_OFF  PORTB &= ~(127)






int main(void)
{
char buffer[50],cnt;
uint32_t x;
double distance=0;
i2c_init();
i2c_lcd_init();

//PA0 = output switch light. PA1 = input. switch for user input. PA2 = input. switch for ball 
DDRA=0;  PORTA=7; 
DDRB=127; // B0-B6 output. for controlling the LEDs

DDRD=(1<<PIN_GREEN);

i2c_lcd_put_string("MEASURE GRAVITY",1);

while(1){
	GREEN_ON;
	if(PINA&0x2){
		while(PINA&0x2)//wait for manual input
			{
			RED_ON;delay_ms(100);RED_OFF;delay_ms(100);
			}  // Wait and flicker
	}
	else if(!(PINA&0x2)){
		while(!(PINA&0x2))//wait for manual input
		{
			RED_ON;delay_ms(100);RED_OFF;delay_ms(100);
		}   // Wait and flicker
	}
	start_timer();                        // start the timer using Timer/Counter1
	GREEN_OFF;

	i2c_lcd_clear();
	i2c_lcd_put_string("DROP!",1);
	
	if(PINA&0x1){while(PINA&0x1);}
	else if(!(PINA&0x1)){while(!(PINA&0x1));}

	x = read_timer();

	distance = (float)(x)/1000.;           //this is actually the time in mS
	i2c_lcd_put_string("Time(ms): ",1);
	ltoa(distance,buffer,10); //10 means decimal.
	i2c_lcd_put_string(buffer,0);

	distance = 0.5*981*distance*distance/1000./1000.; // S = 0.5 * g *  t^2

	i2c_lcd_put_string("Distance(cm): ",2);
	ltoa(distance*10,buffer,10); //
	i2c_lcd_put_string(buffer,0);
    }
}
