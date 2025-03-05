from machine import Pin, SPI
import gc9a01
import vga1_bold_16x32 as font

SCK = 18
MOSI = 23

DC1 = 19
RST1 = 14
CS1 = 33

DC2 = 25
RST2 = 27
CS2 = 13

DISP_EN = 32

disp_en = Pin(32, Pin.OUT)
disp_en.value(1)

spi = SPI(1, baudrate=60000000, sck=Pin(SCK), mosi=Pin(MOSI))

display1 = gc9a01.GC9A01(spi, 240, 240, reset=Pin(RST1, Pin.OUT), cs=Pin(CS1, Pin.OUT), dc=Pin(DC1, Pin.OUT), rotation=3, options=0, buffer_size=0)
display2 = gc9a01.GC9A01(spi, 240, 240, reset=Pin(RST2, Pin.OUT), cs=Pin(CS2, Pin.OUT), dc=Pin(DC2, Pin.OUT), rotation=3, options=0, buffer_size=0)

display1.init()
display2.init()

display1.fill(gc9a01.BLACK)
display2.fill(gc9a01.BLACK)

def display_center_text(font, text, display, fg, bg):
    display.text(
        font,
        text,
        int((display.width()/2) - ((font.WIDTH*len(text)/2))),
        int((display.height()/2) - (font.HEIGHT/2)),
        fg,
        bg
    )

def display_center_write(font, text, display, fg, bg):
    display.write(
        font,
        text,
        int((display.width()/2) - ((display.write_len(font, text)/2))),
        int((display.height()/2) - (font.HEIGHT/2)),
        fg,
        bg
    )
