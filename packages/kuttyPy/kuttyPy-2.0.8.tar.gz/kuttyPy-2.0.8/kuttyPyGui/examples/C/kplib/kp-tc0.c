// kp-tc0.c -- functions for handling the Timer/Counter 0

#include <avr/io.h>

void sqwave_tc0(uint8_t csb, uint8_t ocrval) 
{
// Set TCCR0 in the CTC mode
  TCCR0 = (1 << WGM01) | (1 << COM00) | csb;	
  OCR0 = ocrval;
  TCNT0 = 0;
  DDRB |= (1 << PB3);
}


void pwm_tc0(uint8_t csb, uint8_t ocrval) 
{
// Set TCCR0 in the Fast PWM mode
  TCCR0 =(1 << WGM01) | (1 << WGM00) | (1 << COM01) | csb;
  OCR0 = ocrval;
  TCNT0 = 0;
  DDRB |= (1 << PB3);
}

