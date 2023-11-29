"""
Original source for MicroPython
MicroPython TM1637 quad 7-segment LED display driver
https://github.com/mcauser/micropython-tm1637

Python3 Port
https://github.com/depklyon/raspberrypi-tm1637

MIT License
Copyright (c) 2016-2018 Mike Causer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from time import sleep

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

TM1637_CMD1 = 0x40  # 0x40 data command
TM1637_CMD2 = 0xc0  # 0xC0 address command
TM1637_CMD3 = 0x80  # 0x80 display control command
TM1637_DSP_ON = 0x08  # 0x08 display on
TM1637_DELAY = 0.00000001  # 10us delay between clk/dio pulses
TM1637_MSB = 0x80  # msb is the decimal point or the colon depending on your display

# 0-9, a-z, blank, dash, star
_SEGMENTS = bytearray(
    b'\x3F\x06\x5B\x4F\x66\x6D\x7D\x07\x7F\x6F\x77\x7C\x39\x5E\x79\x71\x3D\x76\x06\x1E\x76\x38\x55\x54\x3F\x73\x67'
    b'\x50\x6D\x78\x3E\x1C\x2A\x76\x6E\x5B\x00\x40\x63')


class TM1637(object):
    """Library for quad 7-segment LED modules based on the TM1637 LED driver."""

    def __init__(self, clk, dio, brightness=7):
        self.clk = clk
        self.dio = dio

        if not 0 <= brightness <= 7:
            raise ValueError("Brightness out of range")
        self._brightness = brightness

        GPIO.setup(self.clk, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.dio, GPIO.OUT, initial=GPIO.LOW)

    def __del__(self):
        pass
        # GPIO.cleanup(self.clk)
        # GPIO.cleanup(self.dio)

    def _start(self):
        GPIO.output(self.clk, GPIO.HIGH)
        GPIO.output(self.dio, GPIO.HIGH)
        GPIO.output(self.dio, GPIO.LOW)
        GPIO.output(self.clk, GPIO.LOW)

    def _stop(self):
        GPIO.output(self.clk, GPIO.LOW)
        GPIO.output(self.dio, GPIO.LOW)
        GPIO.output(self.clk, GPIO.HIGH)
        GPIO.output(self.dio, GPIO.HIGH)

    def _write_data_cmd(self):
        # automatic address increment, normal mode
        self._start()
        self._write_byte(TM1637_CMD1)
        self._stop()

    def _write_dsp_ctrl(self):
        # display on, set brightness
        self._start()
        self._write_byte(TM1637_CMD3 | TM1637_DSP_ON | self._brightness)
        self._stop()

    def _write_byte(self, b):
        for i in range(8):
            GPIO.output(self.dio,(b >> i) & 1)
            sleep(TM1637_DELAY)
            GPIO.output(self.clk, GPIO.HIGH)
            sleep(TM1637_DELAY)
            GPIO.output(self.clk, GPIO.LOW)
            sleep(TM1637_DELAY)

        GPIO.output(self.clk, GPIO.LOW)
        sleep(TM1637_DELAY)
        GPIO.output(self.clk, GPIO.HIGH)
        sleep(TM1637_DELAY)
        GPIO.output(self.clk, GPIO.LOW)

    def brightness(self, val=None):
        """Set the display brightness 0-7."""
        # brightness 0 = 1/16th pulse width
        # brightness 7 = 14/16th pulse width
        if val is None:
            return self._brightness
        if not 0 <= val <= 7:
            raise ValueError("Brightness out of range")

        self._brightness = val
        self._write_data_cmd()
        self._write_dsp_ctrl()

    def write(self, segments, pos=0):
        """Display up to 6 segments moving right from a given position.
        The MSB in the 2nd segment controls the colon between the 2nd
        and 3rd segments."""
        if not 0 <= pos <= 5:
            raise ValueError("Position out of range")
        self._write_data_cmd()
        self._start()
        self._write_byte(TM1637_CMD2 | pos)
        for seg in segments:
            self._write_byte(seg)
        self._stop()
        self._write_dsp_ctrl()

    @staticmethod
    def encode_digit(digit):
        """Convert a character 0-9, a-f to a segment."""
        return _SEGMENTS[digit & 0x0f]

    @staticmethod
    def encode_char(char):
        """Convert a character 0-9, a-z, space, dash or star to a segment."""
        o = ord(char)
        if o == 32:
            return _SEGMENTS[36]  # space
        if o == 42:
            return _SEGMENTS[38]  # star/degrees
        if o == 45:
            return _SEGMENTS[37]  # dash
        if 65 <= o <= 90:
            return _SEGMENTS[o - 55]  # uppercase A-Z
        if 97 <= o <= 122:
            return _SEGMENTS[o - 87]  # lowercase a-z
        if 48 <= o <= 57:
            return _SEGMENTS[o - 48]  # 0-9
        raise ValueError("Character out of range: {:d} '{:s}'".format(o, chr(o)))

    def encode_string(self, string):
        """Convert an up to 4 character length string containing 0-9, a-z,
        space, dash, star to an array of segments, matching the length of the
        source string."""
        segments = bytearray(len(string))
        for i in range(len(string)):
            segments[i] = self.encode_char(string[i])
        return segments

    def hex(self, val):
        """Display a hex value 0x0000 through 0xffff, right aligned."""
        string = '{:04x}'.format(val & 0xffff)
        self.write(self.encode_string(string))

    def number(self, num):
        """Display a numeric value -999 through 9999, right aligned."""
        # limit to range -999 to 9999
        num = max(-999, min(num, 9999))
        string = '{0: >4d}'.format(num)
        self.write(self.encode_string(string))

    def numbers(self, num1, num2, colon=True):
        """Display two numeric values -9 through 99, with leading zeros
        and separated by a colon."""
        num1 = max(-9, min(num1, 99))
        num2 = max(-9, min(num2, 99))
        segments = self.encode_string('{0:0>2d}{1:0>2d}'.format(num1, num2))
        if colon:
            segments[1] |= 0x80  # colon on
        self.write(segments)

    def temperature(self, num):
        if num < -9:
            self.show('lo')  # low
        elif num > 99:
            self.show('hi')  # high
        else:
            string = '{0: >2d}'.format(num)
            self.write(self.encode_string(string))
        self.write([_SEGMENTS[38], _SEGMENTS[12]], 2)  # degrees C

    def dec_temperature(self, num):
        if num < -9.9: # limit to single digit negatives
            self.write([0, 0, 0, 0])
            self.show('lo')  # low
        elif num > 99.9:
            self.write([0, 0, 0, 0])
            self.show('hi')  # high
        else:
            intval = abs(int(num/1))
            if num == 0: # exact zero
                seg1 = 0b00000000
                seg2 = self.encode_digit(0)
                seg3 = self.encode_digit(0)
            else:
                if intval < 10 and num > 0: # single digit positive
                    seg1 = 0b00000000
                    seg2 = self.encode_digit(intval)
                elif num < 0: # negative
                    seg1 = 0b01000000 # '-'
                    seg2 = self.encode_digit(intval)
                else: # two digit (can only be positive)
                    seg1 = self.encode_digit(int(intval/10))
                    seg2 = self.encode_digit(int(num-(int(intval/10)*10)))

                try:
                    seg3 = self.encode_digit(int(str(num).split('.')[1][0])) # will fail if there is no decimal point
                except:
                    seg3 = self.encode_digit(0)
            segments = [seg1, seg2, seg3, _SEGMENTS[38]] # segments and degree character
            segments[1] |= 0x80  # colon as decimal
            self.write(segments)
            
    def show(self, string, colon=False):
        segments = self.encode_string(string)
        if len(segments) > 1 and colon:
            segments[1] |= 128
        self.write(segments[:4])

    def scroll(self, string, delay=250):
        segments = string if isinstance(string, list) else self.encode_string(string)
        data = [0] * 8
        data[4:0] = list(segments)
        for i in range(len(segments) + 5):
            self.write(data[0 + i:4 + i])
            sleep(delay / 1000)


class TM1637Decimal(TM1637):
    """Library for quad 7-segment LED modules based on the TM1637 LED driver.

    This class is meant to be used with decimal display modules (modules
    that have a decimal point after each 7-segment LED).
    """

    def encode_string(self, string):
        """Convert a string to LED segments.

        Convert an up to 4 character length string containing 0-9, a-z,
        space, dash, star and '.' to an array of segments, matching the length of
        the source string."""
        segments = bytearray(len(string.replace('.', '')))
        j = 0
        for i in range(len(string)):
            if string[i] == '.' and j > 0:
                segments[j - 1] |= TM1637_MSB
                continue
            segments[j] = self.encode_char(string[i])
            j += 1
        return segments

if __name__ == "__main__":
    # import time
    tm = TM1637(clk=5, dio=4, brightness=1)

    # all LEDS on "88:88"
    tm.write([127, 255, 127, 127])
    sleep(3)

    # all LEDS off
    tm.write([0, 0, 0, 0])
    sleep(3)

    # show "0123"
    tm.write([63, 6, 91, 79])
    sleep(3)

    # show "3432"
    tm.number(3432)
    sleep(3)

    # show "00:00"
    tm.numbers(0, 0)
    sleep(3)

    # # show "COOL"
    tm.write([0b00111001, 0b00111111, 0b00111111, 0b00111000])
    sleep(3)

    # # show "HELP"
    tm.show('help')
    sleep(3)

    # # display "dEAd", "bEEF"
    tm.hex(0xdead)
    sleep(3)
    
    tm.hex(0xbeef)
    sleep(3)

    # # show "12:59"
    tm.numbers(12, 59)
    sleep(3)

    # # show "-123"
    tm.number(-123)
    sleep(3)

    # # show temperature '24*C'
    tm.temperature(24)
    sleep(3)