from machine import Pin, SPI

import vga1_bold_16x32
import machine

import micropython

import gc9a01

# @micropython.viper
def rgb(color: tuple):
    r, g, b = color
    return (r & 0xF8) | ((g & 0xE0) >> 5) | ((g & 0x1C) << 11) | ((b & 0xF8) << 5)


class Displays:
    SCK = 18
    MOSI = 23

    DC1 = 19
    RST1 = 14
    CS1 = 33

    DC2 = 25
    RST2 = 27
    CS2 = 13

    DISP_EN = 32
    COLOR_LOOKUP: dict[str, dict[str, int]] = {
        "gc9a01": {
            # "black": gc9a01.BLACK,
            # "blue": gc9a01.BLUE,
            # "red": gc9a01.RED,
            # "green": gc9a01.GREEN,
            # "cyan": gc9a01.CYAN,
            # "magenta": gc9a01.MAGENTA,
            # "yellow": gc9a01.YELLOW,
            # "white": gc9a01.WHITE,
        },
        "fbuf": {
            "black": rgb((0, 0, 0)),
            "blue": rgb((0, 0, 255)),
            "red": rgb((255, 0, 0)),
            "green": rgb((0, 255, 0)),
            "cyan": rgb((0, 255, 255)),
            "magenta": rgb((255, 0, 255)),
            "yellow": rgb((255, 255, 0)),
            "white": rgb((255, 255, 255)),
        },
    }

    def __init__(self, spi_freq: int = 80_000_000):
        disp_en = Pin(self.DISP_EN, Pin.OUT)
        disp_en.value(1)

        spi_freq = spi_freq or machine.freq() // 2
        print(f"SPI Frequency: {spi_freq}")
        spi = SPI(1, baudrate=spi_freq, sck=Pin(self.SCK), mosi=Pin(self.MOSI))

        # TODO move to smart config?
        USE_PY_DRIVER = False
        if USE_PY_DRIVER:
            from drivers.gc9a01 import GC9A01 as DisplayDriver
        else:
            from gc9a01 import GC9A01 as DisplayDriver

        self.display1 = DisplayDriver(
            spi,
            240,
            240,
            reset=Pin(self.RST1, Pin.OUT),
            cs=Pin(self.CS1, Pin.OUT),
            dc=Pin(self.DC1, Pin.OUT),
            rotation=3
        )

        self.display2 = DisplayDriver(
            spi,
            240,
            240,
            reset=Pin(self.RST2, Pin.OUT),
            cs=Pin(self.CS2, Pin.OUT),
            dc=Pin(self.DC2, Pin.OUT),
            rotation=3
        )

        self.display1.init()
        self.display2.init()

        self.display1.jpg('/img/bsides_logo.jpg', 0, 0, gc9a01.FAST)
        self.display2.jpg('/img/gigtel_logo.jpg', 0, 0, gc9a01.FAST)

    @staticmethod
    def rgb_to_565(r: int, g: int, b: int):
        return (r & 0xF8) | ((g & 0xE0) >> 5) | ((g & 0x1C) << 11) | ((b & 0xF8) << 5)

    def display_center_text(
        self,
        text: str,
        fg=gc9a01.WHITE,
        bg=gc9a01.BLACK,
        display_index: int = 1,
        font=None,
    ):
        if not font:
            import vga1_bold_16x32
            font = vga1_bold_16x32
        display = self[display_index - 1]
        self.display_text(
            text,
            int((display.width() / 2) - (font.WIDTH * len(text) / 2)),
            int((display.height() / 2) - (font.HEIGHT / 2)),
            fg,
            bg,
            display_index,
            font,
        )

    def display_text(
        self,
        text,
        x,
        y,
        fg=gc9a01.WHITE,
        bg=gc9a01.BLACK,
        display_index: int = 1,
        font=None,
    ):
        if not font:
            import vga1_bold_16x32
            font = vga1_bold_16x32
        display = self[display_index - 1]
        display.text(font, text, x, y, fg, bg)

    def __getitem__(self, index):
        if index == 0:
            return self.display1
        elif index == 1:
            return self.display2
        else:
            raise IndexError("Display index out of range")

    def __len__(self):
        return 2
