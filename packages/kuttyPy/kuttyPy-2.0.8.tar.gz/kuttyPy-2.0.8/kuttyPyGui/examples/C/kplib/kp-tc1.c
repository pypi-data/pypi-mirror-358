// kp-tc1.c -- functions for handling the Timer/Counter 1

#include <avr/io.h>
#include <avr/interrupt.h>

void delay_sec (void)  // idle for 1 seconds, only for 8MHz clock
    {
    volatile uint16_t x, k =1000;
    while(k--) {x=5320; while (x--);}
    }

void sqwave_tc1(uint8_t csb, uint16_t ocra) 
{
		// This can set very low values of freqency on the output
  TCCR1A = (1 << COM1A0);    // Set TCCR1A in the CTC mode
  TCCR1B = (1 << WGM12) | csb;	
  OCR1A = ocra;     // Output Compare register values
  TCNT1 = 0;
  DDRD |= (1 << PD5);   // Set pin OC1A as output
}

void pwm10_tc1(uint8_t csb, uint16_t ocra) 
{
  TCCR1A = (1 << COM1A1) | (1 << WGM11) |(1 << WGM10);  // Set 10bit PWM mode
  TCCR1B = csb;	
  OCR1A = ocra;     // Output Compare register values
  TCNT1 = 0;
  DDRD |= (1 << PD5);   // Set pin OC1A as output
}


//------------------- Frequency measurement ----------------------------

#define MTIME	250 	// We count 100  on TC0

extern void delay_ms (uint16_t k);

uint32_t measure_freq(void)
{ 
  DDRB &= ~(1 << PB1);      // Timer/Counter1 clock in T1 (PB1) as input
  TCCR1B = (1 << CS12) | (1 << CS11) | (1 << CS10); // External clock on T1 pin 
  TCNT1 = 0;			    // Clear TCNT1
  delay_ms(536);
  TCCR1B = 0;               // Stop counter
  return TCNT1 * 2;         // freq = Counts / 500 mS x 2
}

//----------------------- Time interval measurement--------------------------

volatile uint16_t HIWORD;
ISR(TIMER1_COMPA_vect)	// TIMER1 Compare Match A Interrupt
{
TCNT1 = 0;
++HIWORD;
}

void start_timer()
{
/*
When TCNT1 reaches OCR1A, the ISR will run. It will clear TCNT1 and increment HIWORD.
The total time elapsed between start_timer and get_timer = HIWORD * 50000 + TCNT1
*/
 TCCR1B = (1 << CS11);   // Normal mode, with 1MHz clock
 HIWORD = 0;
 OCR1A = 50000;        
 OCR1B = 0xffff;
 TIMSK = (1 <<  OCIE1A);   // Enable compare match interrupt
 TIFR = (1 << OCF1A); 
 TCNT1 = 0;
 sei();
}

uint32_t read_timer()
{
 uint32_t x;
 
 TCCR1B = 0;    // stop TC1 clock
 x = HIWORD * 50000 + TCNT1;
 cli();
 return x;
}

uint32_t r2ftime(uint8_t bit)  
{
// measures rising edge to falling edge time on any bit of PORTB. If no pulse input, program may go in infinite loop
 
 DDRB &= ~(1 << bit);   // set the selected bit as input, on PORT B   
 while( (PINB & (1 << bit)) != 0 ) ;   // Do nothing until the bit is low
 while( (PINB & (1 << bit)) == 0 ) ;   // Wait for a rising edge
 start_timer();
 while( (PINB & (1 << bit)) != 0 ) ;   // Wait for a falling edge
 return read_timer();
}

