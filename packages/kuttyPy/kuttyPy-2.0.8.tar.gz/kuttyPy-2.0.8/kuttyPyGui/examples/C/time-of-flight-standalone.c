/* time of flight measurement of a falling object. 
 * A 5V relay is opened, and the electromagnet is exposed. Its driver pin is connected to B7.
 * RELAY (B7): The program makes B7 HIGH, and therefore the electromagnet is energized.
 * The user now fixes this relay at a fixed height from the floor/table, and attaches
 * a small steel ball to it.
 * Fall Detection Switch : 2 metal plates are used to make a switch connecting PA2 to GND.
 * When the ball falls, the plates will make contact, and PA2 will go LOW.

 * User Input(PA1): A user input switch is connected to PA1 which is internally pulled up. 
 * The measurement begins when the user presses this switch, causing PA1 to go LOW.
 * 		The microcontroller starts a timer when the relay is turned off, and stops it when the contact switch
 * 		is triggered, thereby measuring the time taken for the ball to travel the known distance.
 * Author: jithinbp@gmail.com
 * License : gpl-v3
 * Date 10 sept 2024

 */

#include <avr/kp.h>
#include <avr/interrupt.h>
#include <string.h>
#include <stdlib.h>

#define PIN_RELAY 7
#define RELAY_OFF   PORTB |= (1<<PIN_RELAY)
#define RELAY_ON  PORTB &= ~(1<<PIN_RELAY)

#define INPUT_HIGH  PINA&4

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
DDRA=1;  PORTA=7; 
DDRB=255; // output. for controlling the relay and LEDs

DDRD=(1<<PIN_GREEN);

i2c_lcd_put_string("MEASURE GRAVITY",1);

while(1){
	RELAY_ON;
	GREEN_ON;
	while(PINA&0x2)//wait for manual input
		{RED_ON;delay_ms(100);RED_OFF;delay_ms(100);} ;   // Wait and flicker

	i2c_lcd_clear();
	i2c_lcd_put_string("DROP!",1);
	GREEN_OFF; RELAY_OFF;
	start_timer();                        // start the timer using Timer/Counter1
	while(INPUT_HIGH) ;   // Wait for the ball to hit the switch between PA0 and GND
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
