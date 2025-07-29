rm -f libkp.a *.o
avr-gcc -g -O2 -mmcu=atmega32a -c kp-adc.c kp-utils.c kp-uart.c kp-tc0.c kp-tc1.c kp-tc2.c kp-lcd.c kp-i2c.c kp-i2c-lcd.c
avr-ar -sr libkp.a kp-utils.o kp-adc.o kp-uart.o kp-tc0.o kp-tc1.o kp-tc2.o kp-lcd.o kp-i2c.o kp-i2c-lcd.o
sudo cp libkp.a /usr/lib/avr/lib/
sudo cp kp.h /usr/lib/avr/include/avr
rm -f *.o *.map *.lst *.hex
