// Header files for libkp
#ifndef KP_H
#define KP_H


#include <avr/io.h>


#define DEBUG_LOG			0
#define SUCCESS				0

// For KuttypyPlus
#define TW_SCL_PIN			PORTC0
#define TW_SDA_PIN			PORTC1

#define TW_SLA_W(ADDR)		((ADDR << 1) | TW_WRITE)
#define TW_SLA_R(ADDR)		((ADDR << 1) | TW_READ)
#define TW_READ_ACK			1
#define TW_READ_NACK		0


// kp-lcd.c, 16x2 charcter LCD on port C of Atmega32
extern void lcd_init(void);
extern void lcd_clear(void);
extern void lcd_put_char (char c);
extern void lcd_put_string(char *a);
extern void lcd_put_byte(uint8_t val);
extern void lcd_put_int(uint16_t val);
extern void lcd_put_long(uint32_t val);
extern void lcd_put_float(float val, uint8_t ndec);


//kp-i2c.c
extern unsigned char I2CStart(void);
extern void I2CWait();
extern void I2CStop();
extern unsigned char I2CSend(unsigned char );

extern void i2c_init(void);
extern uint8_t i2c_scan(uint8_t *);
extern uint8_t i2c_write(uint8_t , uint8_t *, uint8_t );
extern uint8_t i2c_read(uint8_t , uint8_t , uint8_t *, uint8_t );

// kp-i2c-lcd.c
extern unsigned int i2c_lcd_init(void);
extern void i2c_lcd_write_cmd(unsigned char);
extern void i2c_lcd_write_cmd_arg(unsigned char , unsigned char );
extern void i2c_lcd_strobe(unsigned char);

extern void i2c_lcd_write_four_bits(unsigned char);
extern void i2c_lcd_write(unsigned char);

extern void i2c_lcd_write_char(unsigned char);
extern void i2c_lcd_put_string(char *, unsigned char );
extern void i2c_lcd_put_shifted_string(char *, unsigned char , unsigned int );
extern void i2c_lcd_clear();


// kp-adc.c
extern void adc_enable (void);				
extern uint16_t read_adc (uint8_t ch);
extern uint8_t read_adc_8bit (uint8_t ch);

// kp-uart.c
extern void uart_init(uint16_t baud);
extern void uart_send_byte(uint8_t);
extern uint8_t uart_recv_byte(void);
extern void uart_send_string(char *);
extern void uart_send_byte_ascii(uint8_t );



// kp-utils.c
extern void delay (uint16_t k);
extern void delay_us (uint16_t k);
extern void delay_100us (uint16_t k);
extern void delay_ms (uint16_t k);
extern void delay_sec (uint16_t k);

// kp-tc0.c
extern void sqwave_tc0(uint8_t csb, uint8_t ocrval);
extern void pwm_tc0(uint8_t csb, uint8_t ocrval);

// kp-tc1.c
extern void sqwave_tc1(uint8_t csb, uint16_t ocra);
extern void pwm10_tc1(uint8_t csb, uint16_t ocra); 
extern uint32_t measure_freq(void);
extern uint32_t r2ftime(uint8_t bit);
extern void start_timer(void);
extern uint32_t read_timer(void);
// kp-tc2.c
extern uint32_t set_sqr_tc2(uint32_t freq);

#endif

