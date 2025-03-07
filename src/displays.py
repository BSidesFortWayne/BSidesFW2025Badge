from machine import Pin, SPI # type: ignore
import gc9a01 # type: ignore
import vga1_bold_16x32 # type: ignore

SCK = 18
MOSI = 23

DC1 = 19
RST1 = 14
CS1 = 33

DC2 = 25
RST2 = 27
CS2 = 13

# Create a Pin object on GPIO32 configured for output
IO32 = Pin(32, Pin.OUT)

# Set GPIO32 high to turn on the displays
IO32.value(1)

DISP_EN = 32

disp_en = Pin(32, Pin.OUT)
disp_en.value(1)

spi = SPI(1, baudrate=60000000, sck=Pin(SCK), mosi=Pin(MOSI))

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

def display_center_text(text, fg, bg, display_index: int = 1, font=vga1_bold_16x32):
    display = display_map[display_index]
    display.text(
        font,
        text,
        int((display.width()/2) - ((font.WIDTH*len(text)/2))),
        int((display.height()/2) - (font.HEIGHT/2)),
        fg,
        bg
    )

