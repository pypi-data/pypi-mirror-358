/*
 * File:   12chardisplay.c
 * Author: jithin
 *
 * Created on July 30, 2023, 5:37 PM
 */

#include <avr/io.h>
#include<string.h>
#include <stdbool.h>

#include "kp.h"



#define LCD_DELAY 50 // Delay in uS for the ENable pin pulsing.
// flags for backlight control
#define LCD_BACKLIGHT 0x08
#define LCD_NOBACKLIGHT 0x00

#define En 0b00000100 // Enable bit
#define Rw 0b00000010 // Read/Write bit
#define Rs 0b00000001 // Register select bit

#define LCD_ADDRESS_DISABLED 0
#define LCD_ADDRESS_A 63
#define LCD_ADDRESS_B 39

#define RWBIT 4 // Read/Write 
#define RSBIT 5 // Register select 


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

#define pullup_en 1

typedef enum {
    TW_FREQ_100K,
    TW_FREQ_250K,
    TW_FREQ_400K
} twi_freq_mode_t;


/*-----I2C----*/


static unsigned char address=LCD_ADDRESS_DISABLED;


unsigned int i2c_lcd_init(void){
    DDRC  |= (1 << TW_SDA_PIN) | (1 << TW_SCL_PIN);
    if (pullup_en)
    {

	    PORTC |= (1 << TW_SDA_PIN) | (1 << TW_SCL_PIN);
    }
    else
    {
	    PORTC &= ~((1 << TW_SDA_PIN) | (1 << TW_SCL_PIN));
    }
    DDRC  &= ~((1 << TW_SDA_PIN) | (1 << TW_SCL_PIN));

    /* Set bit rate register 12 and prescaler to 1 resulting in
    SCL_freq = 8MHz/(16 + 2*12*1) = 200KHz	*/
    TWBR = 12;


    delay_us(200);

    //Search LCD

    I2CStart();
    I2CSend(LCD_ADDRESS_A<<1);
    if((TWSR&0xFC) == 0x18) //LCD Found
        address = LCD_ADDRESS_A;
    I2CStop();

    I2CStart();
    I2CSend(LCD_ADDRESS_B<<1);
    if((TWSR&0xFC) == 0x18) //LCD Found
        address = LCD_ADDRESS_B;
    I2CStop();

    delay_us(100);


    i2c_lcd_write(0x03);
    i2c_lcd_write(0x03);
    i2c_lcd_write(0x03);
    i2c_lcd_write(0x02); 

    i2c_lcd_write(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE);
    i2c_lcd_write(LCD_DISPLAYCONTROL | LCD_DISPLAYON);
    i2c_lcd_write(LCD_CLEARDISPLAY);
    i2c_lcd_write(LCD_ENTRYMODESET | LCD_ENTRYLEFT);    
    delay_us(10000);
    
    return address;
    
}



void i2c_lcd_write_cmd(unsigned char cmd){ 
    if(address == LCD_ADDRESS_DISABLED)return;

        I2CStart();
        I2CSend(address<<1); //default address for PCA8547AT IO expander
        I2CSend(cmd&0xFF);     //
        I2CStop();               
    delay_us(1000);
}

void i2c_lcd_write_cmd_arg(unsigned char cmd, unsigned char arg){ 
    if(address == LCD_ADDRESS_DISABLED)return;

    I2CStart();
    I2CSend(address<<1); //default address for PCA8547AT IO expander
    I2CSend(cmd&0xFF);     //
    I2CSend(arg&0xFF);     //
    I2CStop();               
    delay_us(1000);
}

void i2c_lcd_strobe(unsigned char data){
    i2c_lcd_write_cmd( (data&0xFF) | En | LCD_BACKLIGHT);
    delay_us(100);
    i2c_lcd_write_cmd((( (data&0xFF) & ~En) | LCD_BACKLIGHT));
    delay_us(500);
}

void i2c_lcd_write_four_bits(unsigned char data){   //USED ONLY BY I2C LCD for now.     
	    i2c_lcd_write_cmd((data&0xFF) | LCD_BACKLIGHT); 
	    i2c_lcd_strobe(data);
}

// write a command to lcd
void i2c_lcd_write(unsigned char cmd){
    if(address == LCD_ADDRESS_DISABLED)return;
    
    i2c_lcd_write_cmd( (cmd & 0xF0)           | LCD_BACKLIGHT);
    i2c_lcd_write_cmd( (cmd & 0xF0)      | En | LCD_BACKLIGHT); delay_us(LCD_DELAY); // EN ON
    i2c_lcd_write_cmd(                          LCD_BACKLIGHT); delay_us(LCD_DELAY); // EN OFF

    i2c_lcd_write_cmd( ((cmd<<4) & 0xF0)      | LCD_BACKLIGHT);
    i2c_lcd_write_cmd( ((cmd<<4) & 0xF0) | En | LCD_BACKLIGHT); delay_us(LCD_DELAY); // EN ON
    i2c_lcd_write_cmd(                          LCD_BACKLIGHT); delay_us(LCD_DELAY); // EN OFF
    
}

// write a character to lcd
void i2c_lcd_write_char(unsigned char cmd){
    if(address == LCD_ADDRESS_DISABLED)return;

    i2c_lcd_write_cmd( Rs | (cmd & 0xF0)           | LCD_BACKLIGHT);
    i2c_lcd_write_cmd( Rs | (cmd & 0xF0)      | En | LCD_BACKLIGHT); delay_us(LCD_DELAY); // EN ON
    i2c_lcd_write_cmd(                               LCD_BACKLIGHT); delay_us(LCD_DELAY); // EN OFF

    i2c_lcd_write_cmd( Rs | ((cmd<<4) & 0xF0)      | LCD_BACKLIGHT);
    i2c_lcd_write_cmd( Rs | ((cmd<<4) & 0xF0) | En | LCD_BACKLIGHT); delay_us(LCD_DELAY); // EN ON
    i2c_lcd_write_cmd(                               LCD_BACKLIGHT); delay_us(LCD_DELAY); // EN OFF

}



// put string function
void i2c_lcd_put_string(char *s, unsigned char line){
    int xpos=0;
    if(line == 1)
	    i2c_lcd_write(0x80);
    else if(line == 2)
	    i2c_lcd_write(0xC0);
    else if(line == 3)
	    i2c_lcd_write(0x94);
    else if(line == 4)
	    i2c_lcd_write(0xD4);

    for (int i = 0; i < strlen(s) && i<32; i++){
	    if(xpos==16 && line==1){
		    i2c_lcd_write(0x14); //Move to the next line
		    xpos=0;
	    }
	    if( *(s+i)=='\n' && line==1){
		    i2c_lcd_write(0xC0); //Move to the next line
		    xpos=0;                
	    }else
		    i2c_lcd_write_char(*(s+i));
	    xpos++;
    }

}


void i2c_lcd_put_shifted_string(char *s, unsigned char line, unsigned int xpos){
    if(address == LCD_ADDRESS_DISABLED)return;

    unsigned char row_offsets[] = {0x00, 0x40, 0x14, 0x54};
    
    i2c_lcd_write(0xC8);
    	    
    for (int i = 0; i < strlen(s) && i<32; i++){
        i2c_lcd_write_char(*(s+i));
        xpos++;
    }
}

//clear lcd and set to home
void i2c_lcd_clear(){
    if(address == LCD_ADDRESS_DISABLED)return;

    i2c_lcd_write(LCD_CLEARDISPLAY);
    i2c_lcd_write(LCD_RETURNHOME);
}

/*
int main()
{
uint32_t f;

i2c_lcd_init();


while(1)
   {
   f = measure_freq();   // Measures on T1 (PB1)
   i2c_lcd_clear();
   i2c_lcd_put_string("f=",0);
   delay_ms(200);
   }
}

*/


