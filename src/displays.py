from machine import Pin, SPI
import gc9a01
import vga1_bold_16x32 as font

SCK = 18
MOSI = 23

DC1 = 22
RST1 = 14
CS1 = 5

DC2 = 21
RST2 = 27
CS2 = 4


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
