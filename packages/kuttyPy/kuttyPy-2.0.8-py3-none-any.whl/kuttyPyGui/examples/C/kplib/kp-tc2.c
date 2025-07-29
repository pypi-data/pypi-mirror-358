// kp-tc2.c -- functions for handling the Timer/Counter 2

#include <avr/io.h>
#include <avr/interrupt.h>

//------------------------- Square wave on TC2 -------------------------
#define FLIMIT  4000000          // 8 MHz clock /2
static uint16_t f[] = {1,8,32,64,128,256,1024};
 
uint32_t set_sqr_tc2(uint32_t freq)  // freq must be from 15  to 100000 Hz, no checking done 
{
	uint32_t tmp;
	uint8_t ocr, k;

	DDRD |= (1 << PD7);    // Make PD7 as output
  	k = 0;
  	while(k < 7) 
  	  {
      tmp = FLIMIT / f[k];	// maximum value for the chosen prescaler
      if (tmp/freq <= 256) 
        {
      	TCCR2 = (1 << WGM21) | (1 << COM20) | (k+1);	// CTC mode
      	ocr = tmp/freq;
      	tmp = tmp/ocr;	// the value actually set
      	if (ocr) 
        	--ocr;
      	OCR2 = ocr;
      	return tmp;
        }
      k = k + 1;
  }
	return 0;  
}

