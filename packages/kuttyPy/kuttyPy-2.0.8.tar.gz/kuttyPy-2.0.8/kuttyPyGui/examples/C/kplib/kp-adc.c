/* adc.c -- routines for handling the Analog to Digital converter

   Copyright (C) 2008 Ajith Kumar, Inter-University Accelerator Centre,
   New Delhi and Pramode C.E, GnuVision.com.

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3, or (at your option)
   any later version.
*/

#include <avr/io.h>

#define BITVAL(bit)  (1 << (bit))
#define SETBIT(sfr, bit) (_SFR_BYTE(sfr) |= BITVAL(bit))
#define CLRBIT(sfr, bit) (_SFR_BYTE(sfr) &= ~BITVAL(bit))

#define REF_EXT	0	    // Feed reference voltage externally
#define REF_INT	(3<<6)	    // use the 2.56 V internal reference
#define REF_AVCC	(1<<6)	    // Connect AVCC internally to reference
#define ADMAX	7	    // channels 0 to 7 
#define ADC_SPEED	7	    // ADCClk = (8 MHz/ 128) = 62.5 KHz =>208 usec


void adc_enable(void)	    // Also sets reference abd conversion speed
{
    SETBIT(ADCSRA, ADEN);	    // Enable the ADC
    CLRBIT(ADMUX, REFS0);         // Clear refval bits
    CLRBIT(ADMUX, REFS1);
    SETBIT(ADMUX, REFS0);         // Select AVCC by default
    ADCSRA |= ADC_SPEED;	    // Set to the lowest speed
}

void adc_disable(void)
{
	ADCSRA = 0;					// Disable the ADC
}


void adc_set_ref(uint8_t val)   // 0 : external, 1 : AVCC, 2 : Internal 2.56V
{
    CLRBIT(ADMUX, REFS0);               // Clear refval bits
    CLRBIT(ADMUX, REFS1);
    if (val == 1)
      ADMUX |= REF_AVCC;		// Use AVCC as reference
    else if (val == 2)
        {
        SETBIT(ADMUX, REFS0);               // Set both S0 and S1
        SETBIT(ADMUX, REFS1);
    }
}

uint16_t read_adc(uint8_t ch)	// Returns 10 bit number
{
	uint16_t res;

	if (ch > ADMAX) return 0;
	ADMUX &= ~0x1F ;                        // Clear the channel bits
	ADMUX |=   ch;		          // Set the desired channel
	CLRBIT(ADMUX, ADLAR);	          // Clear Left adjust  
	SETBIT(ADCSRA, ADSC);	          // start conversion
	while ( !(ADCSRA & (1<<ADIF)) ) ;	// wait for ADC conversion
	ADCSRA |= ADIF;
          res = ADCL;                             // ADCL must be read first
	return (ADCH << 8) | res;
}

uint8_t read_adc_8bit(uint8_t ch)	// Returns 10 bit number
{

	if (ch > ADMAX) return 0;
	ADMUX &= ~0x1F ;                 // Clear the channel bits
	ADMUX |=   ch;					// Set the desired channel
	SETBIT(ADMUX, ADLAR);		    // Select Left adjust  
	SETBIT(ADCSRA, ADSC);			// start conversion
	while ( !(ADCSRA & (1<<ADIF)) ) ;	// wait for ADC conversion
	ADCSRA |= ADIF;
          return ADCH;
}

