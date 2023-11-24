#!/usr/bin/env python
#
# GrovePi Example for using the Grove - LCD RGB Backlight (http://www.seeedstudio.com/wiki/Grove_-_LCD_RGB_Backlight)
#
# The GrovePi connects the Raspberry Pi and Grove sensors.  You can learn more about GrovePi here:  http://www.dexterindustries.com/GrovePi
#
# Have a question about this example?  Ask on the forums here:  http://forum.dexterindustries.com/c/grovepi
#
# History
# ------------------------------------------------
# Author	Date      		Comments
# 						  	Initial Authoring
# Karan		7 Jan 16		Library updated to add a function to update the text without erasing the screen
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/DexterInd/GrovePi/blob/master/LICENSE

#
# NOTE:
# 	Just supports setting the backlight colour, and
# 	putting a single string of text onto the display
# 	Doesn't support anything clever, cursors or anything

import sys
import time

class rgb_lcd:
    def __init__(self, rgb_addr=0x30, text_addr=0x3e):
        if sys.platform == 'uwp':
            import winrt_smbus as smbus
            self.bus = smbus.SMBus(1)
        else:
            import smbus
            import RPi.GPIO as GPIO
            rev = GPIO.RPI_REVISION
            if rev == 2 or rev == 3:
                self.bus = smbus.SMBus(1)
            else:
                self.bus = smbus.SMBus(0)

        # this device has two I2C addresses
        self.DISPLAY_RGB_ADDR = rgb_addr
        self.DISPLAY_TEXT_ADDR = text_addr

    # set backlight to (R,G,B) (values from 0..255 for each)
    def setRGB(self, r, g, b):
        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR,0,0)
        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR,1,0)
        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR,0x08,0xaa)
        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR,4,r)
        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR,3,g)
        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR,2,b)

    # send command to display (no need for external use)
    def textCommand(self, cmd):
        self.bus.write_byte_data(self.DISPLAY_TEXT_ADDR,0x80,cmd)

    # set display text \n for second line(or auto wrap)
    def setText(self, text):
        self.textCommand(0x01) # clear display
        time.sleep(.05)
        self.textCommand(0x08 | 0x04) # display on, no cursor
        self.textCommand(0x28) # 2 lines
        time.sleep(.05)
        count = 0
        row = 0
        for c in text:
            if c == '\n' or count == 16:
                count = 0
                row += 1
                if row == 2:
                    break
                self.textCommand(0xc0)
                if c == '\n':
                    continue
            count += 1
            self.bus.write_byte_data(self.DISPLAY_TEXT_ADDR,0x40,ord(c))

    #Update the display without erasing the display
    def setText_norefresh(self, text):
        self.textCommand(0x02) # return home
        time.sleep(.05)
        self.textCommand(0x08 | 0x04) # display on, no cursor
        self.textCommand(0x28) # 2 lines
        time.sleep(.05)
        count = 0
        row = 0
        while len(text) < 32: #clears the rest of the screen
            text += ' '
        for c in text:
            if c == '\n' or count == 16:
                count = 0
                row += 1
                if row == 2:
                    break
                self.textCommand(0xc0)
                if c == '\n':
                    continue
            count += 1
            self.bus.write_byte_data(self.DISPLAY_TEXT_ADDR,0x40,ord(c))

    # Create a custom character (from array of row patterns)
    def create_char(self, location, pattern):
        """
        Writes a bit pattern to LCD CGRAM

        Arguments:
        location -- integer, one of 8 slots (0-7)
        pattern -- byte array containing the bit pattern, like as found at
                https://omerk.github.io/lcdchargen/
        """
        location &= 0x07 # Make sure location is 0-7
        self.textCommand(0x40 | (location << 3))
        self.bus.write_i2c_block_data(self.DISPLAY_TEXT_ADDR, 0x40, pattern)

# example code
if __name__ == "__main__":
    rgb_lcd_instance = rgb_lcd()
    rgb_lcd_instance.setText("Hello world\nThis is an LCD test")
    rgb_lcd_instance.setRGB(0,128,64)
    time.sleep(2)
    for c in range(0,255):
        rgb_lcd_instance.setText_norefresh("Going to sleep in {}...".format(str(c)))
        rgb_lcd_instance.setRGB(c,255-c,0)
        time.sleep(0.1)
    rgb_lcd_instance.setRGB(0,255,0)
    rgb_lcd_instance.setText("Bye bye, this should wrap onto next line")
