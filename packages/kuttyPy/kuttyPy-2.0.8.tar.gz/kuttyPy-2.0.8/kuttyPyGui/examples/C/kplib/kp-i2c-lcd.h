

// This is a guard condition so that contents of this file are not included
// more than once.  
#ifndef DISPLAY_HEADER_H
#define	DISPLAY_HEADER_H

#define BYTE unsigned char
typedef BYTE bool;



#define LCD_DELAY 450 // Delay in uS for the ENable pin pulsing.
// flags for backlight control
#define LCD_BACKLIGHT 0x08
#define LCD_NOBACKLIGHT 0x00

#define En 0b00000100 // Enable bit
#define Rw 0b00000010 // Read/Write bit
#define Rs 0b00000001 // Register select bit


#define LCD_ADDRESS_DISABLED 0
#define LCD_ADDRESS_PARALLEL 1
#define LCD_ADDRESS_A 63
#define LCD_ADDRESS_B 39


#define EN_PARALLEL _LATA9
#define RWLAT _LATC4 // Read/Write 
#define RSLAT _LATC5 // Register select 

#define RWBIT 4 // Read/Write 
#define RSBIT 5 // Register select 


void Delay_us(unsigned int delay);

void initI2C(void);
void I2CStart();

void I2CStop();

void I2CRestart();

void I2CAck();

void I2CNak();

void I2CWait();

void I2CSend(unsigned char dat);

unsigned char I2CRead(bool ack);
void write_dac(unsigned int lsb); //MCP4725 1 channel DAC




// PCF8547AT commands
#define LCD_CLEARDISPLAY 0x01
#define LCD_RETURNHOME 0x02
#define LCD_ENTRYMODESET 0x04
#define LCD_DISPLAYCONTROL 0x08
#define LCD_FUNCTIONSET 0x20

#define LCD_SETDDRAMADDR 0x80

// flags for display entry mode
#define LCD_ENTRYLEFT 0x02

// flags for display on/off control
#define LCD_DISPLAYON 0x04
#define LCD_INC 0x06

// flags for function set
#define LCD_4BITMODE 0x00
#define LCD_2LINE 0x08
#define LCD_5x8DOTS 0x00


void write_cmd(unsigned char cmd);
void write_cmd_arg(unsigned char cmd, unsigned char arg);

void lcd_strobe(unsigned char data);

void lcd_write_four_bits(unsigned char data);

// write a command to lcd
void lcd_write(unsigned char cmd);

// write a character to lcd
void lcd_write_char(unsigned char cmd);

unsigned int initLCD();
void init_lcd_cmds();
// put string function
void lcd_display_string(char *s, unsigned char line);
// put string function
void lcd_display_shifted_string(char *s, unsigned char line, unsigned int xpos);

//clear lcd and set to home
void lcd_clear();

#endif	
