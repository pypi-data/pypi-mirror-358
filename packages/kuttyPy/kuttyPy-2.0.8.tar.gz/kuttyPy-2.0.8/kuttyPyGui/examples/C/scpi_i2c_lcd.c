/*
*/

#include <avr/interrupt.h>
#include <string.h>
#include "kp.h"   // Include file for I/O operations


#define BUFFER_SIZE 64     // Size of the input buffer

volatile char rx_buffer[BUFFER_SIZE];  // Input buffer for received commands
char mystr[100];
volatile uint8_t rx_index = 0;         // Buffer index
volatile float v;
volatile uint16_t data;
// Function prototypes
void process_command(void);
void clear_buffer(void);

// Clear the input buffer
void clear_buffer(void) {
    memset((char*)rx_buffer, 0, BUFFER_SIZE);  // Clear buffer
    rx_index = 0;  // Reset index
}

// Process the command received in rx_buffer
void process_command(void) {
    i2c_lcd_clear();
    i2c_lcd_put_string(rx_buffer,1);

    if (strncmp(rx_buffer, "*IDN?\n", rx_index) == 0) {
        uart_send_string("KUTTYPY VOLTMETER\n");

    } else if(strncmp(rx_buffer, "MEAS:0?\n", rx_index) == 0) {
	read_and_send(0);
    } else if(strncmp(rx_buffer, "MEAS:1?\n", rx_index) == 0) {
	read_and_send(1);
    } else if(strncmp(rx_buffer, "MEAS:2?\n", rx_index) == 0) {
	read_and_send(2);
    } else if(strncmp(rx_buffer, "MEAS:3?\n", rx_index) == 0) {
	read_and_send(3);
    } else if(strncmp(rx_buffer, "MEAS:4?\n", rx_index) == 0) {
	read_and_send(4);
    } else if(strncmp(rx_buffer, "MEAS:5?\n", rx_index) == 0) {
	read_and_send(5);
    } else if(strncmp(rx_buffer, "MEAS:6?\n", rx_index) == 0) {
	read_and_send(6);
    } else if(strncmp(rx_buffer, "RED:ON\n", rx_index) == 0) {
	DDRB=255;PORTB=255;
    } else if(strncmp(rx_buffer, "RED:OFF\n", rx_index) == 0) {
	DDRB=255;PORTB=0;
    } 
     else {
        uart_send_string("Unknown command\n");
    }
}

void read_and_send(uint8_t chan){
          sprintf(mystr,"%d",read_adc(chan));
          uart_send_string(mystr);
          uart_send_string("\n");
	i2c_lcd_put_string(mystr,2);
}


// UART RX Complete interrupt service routine
ISR(USART_RXC_vect) {
    char received_char = UDR;  // Read the received character
    if (rx_index < BUFFER_SIZE - 1) {
        rx_buffer[rx_index++] = received_char;  // Store the received character in the buffer
    }

    if (received_char == '\n') {  // Check for newline termination
        rx_buffer[rx_index] = '\0';  // Null-terminate the string
    }
}


int main (void)
{
DDRB=255;
DDRA=0;
PORTA=255;
i2c_init();
i2c_lcd_init();
uart_init(38400);
adc_enable();

UCSRB|= (1<<RXCIE); //enable interrupts

i2c_lcd_put_string("SCPI VOLTMETER",1);

sei();        // Enable global interrupts

uart_send_string("ATmega32 SCPI Voltmeter ready\n");

    while (1) {
        if (rx_buffer[rx_index - 1] == '\n') {  // Check if newline is received
            process_command();                 // Process the command
            clear_buffer();                    // Clear the buffer for the next command
        }
    }


return 0;
}