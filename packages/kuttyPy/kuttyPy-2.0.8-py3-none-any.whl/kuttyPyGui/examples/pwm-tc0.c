#include <avr/kp.h>

uint8_t csb = 2;           // Clock select bits 
uint8_t ocrval = 63;       // Output Compare register vaule

int main() 
{ 
pwm_tc0(csb, ocrval);
}