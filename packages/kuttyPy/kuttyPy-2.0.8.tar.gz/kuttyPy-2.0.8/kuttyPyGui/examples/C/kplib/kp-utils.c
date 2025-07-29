/* utils.c -- various utilities for microHOPE

   Copyright (C) 2008 Ajith Kumar, Inter-University Accelerator Centre,

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3, or (at your option)
   any later version.
*/

#include <avr/io.h>

void delay(uint16_t k)
{
    volatile uint16_t x = k;
    while(x)
        --x;
}

void delay_us(uint16_t k) // not correct
{
    volatile uint16_t x = k;
    while(x)
        --x;
}


void delay_100us (uint16_t k)  	 // k* 100 usecs delay, valid only for 8MHz clock
{
  volatile uint16_t x;
  while (k--) {x=52; while (x--);}
}

void delay_ms (uint16_t k)  // idle for k milliseconds, only for 8MHz clock
    {
    volatile uint16_t x;
    while(k--) {x=532; while (x--);}
    }
    

// Converts an 8bit integer to 3 digit decimal form.
void b2a(int b, char* a)
{
uint8_t d1,d2,d3;
char *p = a;

d3 = 0;
while (b >= 100)
       {
	++d3;
	b -= 100;
	}
if (d3) *p++ = d3 + '0';

d2 = 0;
while (b >= 10)
       {
	++d2;
	b -= 10;
	}
if (d3 | d2) *p++ = d2 + '0';

d1 = 0;
while (b > 0)
       {
	++d1;
	b -= 1;
	}
*p++ =  d1 + '0';
*p = '\0';
}


// Converts an 16bit integer to 5 digit decimal form.
void b2aa(int b, char* a)
{
uint8_t d1,d2,d3,d4,d5;
char *p = a;

d5 = 0;
while (b >= 10000)
       {
	++d5;
	b -= 10000;
	}
if(d5) *p++ = d5 + '0';

d4 = 0;
while (b >= 1000)
       {
	++d4;
	b -= 1000;
	}
if (d5 | d4) *p++ = d4 + '0';

	
d3 = 0;
while (b >= 100)
       {
	++d3;
	b -= 100;
	}
if (d5 | d4 | d3) *p++ = d3 + '0';

d2 = 0;
while (b >= 10)
       {
	++d2;
	b -= 10;
	}
if (d5 | d4 | d3 | d2) *p++ = d2 + '0';

d1 = 0;
while (b > 0)
       {
	++d1;
	b -= 1;
	}
*p++ =  d1 + '0';
*p = '\0';
}

