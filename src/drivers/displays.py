from machine import Pin, SPI
import gc9a01 
import vga1_bold_16x32

SCK = 18
MOSI = 23

DC1 = 19
RST1 = 14
CS1 = 33

DC2 = 25
RST2 = 27
CS2 = 13

DISP_EN = 32

disp_en = Pin(DISP_EN, Pin.OUT)
disp_en.value(1)

reset = Pin(RST1, Pin.OUT)
cs=Pin(CS1, Pin.OUT)
dc=Pin(DC1, Pin.OUT)

spi = SPI(1, baudrate=60_000_000, sck=Pin(SCK), mosi=Pin(MOSI))

display1 = gc9a01.GC9A01(spi, 240, 240, reset=Pin(RST1, Pin.OUT), cs=Pin(CS1, Pin.OUT), dc=Pin(DC1, Pin.OUT), rotation=3, options=0, buffer_size=0)
display2 = gc9a01.GC9A01(spi, 240, 240, reset=Pin(RST2, Pin.OUT), cs=Pin(CS2, Pin.OUT), dc=Pin(DC2, Pin.OUT), rotation=3, options=0, buffer_size=0)

display1.init()
display2.init()

display1.fill(gc9a01.BLACK)
display2.fill(gc9a01.BLUE)

display_map = {
    1: display1,
    2: display2
}

def display_center_text(text, fg = gc9a01.WHITE, bg = gc9a01.BLACK, display_index: int = 1, font=vga1_bold_16x32
):
    display = display_map[display_index]
    display_text(
        text,
        int((display.width()/2) - ((font.WIDTH*len(text)/2))),
        int((display.height()/2) - (font.HEIGHT/2)),
        fg,
        bg,
        display_index,
        font
    )


def display_text(text, x, y, fg = gc9a01.WHITE, bg = gc9a01.BLACK, display_index: int = 1, font=vga1_bold_16x32):
    display = display_map[display_index]
    display.text(font, text, x, y, fg, bg)