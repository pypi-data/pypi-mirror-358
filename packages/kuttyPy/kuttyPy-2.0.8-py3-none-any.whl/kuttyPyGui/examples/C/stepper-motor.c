// Connect pins B0 to B3 for the motor driver input.
/*
wave drive sequence
Step   B0  B1  B2  B3   Decimal
  1     1   0   0   0      1
  2     0   1   0   0      2
  3     0   0   1   0      4
  4     0   0   0   1      8
  5     1   0   0   0      1  (Repeat)


Full Step

Step   B0  B1  B2  B3   Decimal
  1     1   1   0   0      3
  2     0   1   1   0      6
  3     0   0   1   1     12
  4     1   0   0   1      9
  5     1   1   0   0      3  (Repeat)


Half Step  ( used in the C code below )

Step   B0  B1  B2  B3   Decimal
  1     1   0   0   0      1
  2     1   1   0   0      3
  3     0   1   0   0      2
  4     0   1   1   0      6
  5     0   0   1   0      4
  6     0   0   1   1     12
  7     0   0   0   1      8
  8     1   0   0   1      9
  9     1   0   0   0      1  (Repeat)


*/


#include<avr/kp.h>

#define DELAY 5
#define STEPS 200
int main (void)
  {
DDRB = 15;  //For controlling the stepper motor
uint8_t steps[]={0b1100,0b0110,0b0011,0b1001}; // 12,6,3,9
uint16_t pos = 0;
  for(;;)
	{
	for(pos=0;pos<STEPS;pos++){
		PORTB=steps[2];
		delay_ms(DELAY);
		PORTB=steps[1];
		delay_ms(DELAY);
		PORTB=steps[0];
		delay_ms(DELAY);
		PORTB=steps[3];
		delay_ms(DELAY);
		}
	for(pos=0;pos<STEPS;pos++){
		PORTB=steps[0];
		delay_ms(DELAY);
		PORTB=steps[1];
		delay_ms(DELAY);
		PORTB=steps[2];
		delay_ms(DELAY);
		PORTB=steps[3];
		delay_ms(DELAY);
		}
  }
return 0;
}
