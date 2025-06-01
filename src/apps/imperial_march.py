# import asyncio
from apps.app import BaseApp
from machine import Pin, PWM
from time import sleep #, ticks_ms, ticks_diff
from gc9a01 import color565
import vga1_bold_16x32
import neopixel
# import math

class ImperialMarch(BaseApp):
    name = "Imperial March"

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.display = self.controller.bsp.displays.display1
        self.display2 = self.controller.bsp.displays.display2
        self.pin_piezo = Pin(15, Pin.OUT)
        self.leds = neopixel.NeoPixel(Pin(26), 7)
        self.counter = 0

        self.display.fill(color565(0, 0, 0))
        self.display.text(vga1_bold_16x32, "Imperial March", 5, 100, color565(255, 0, 0), color565(0, 0, 0))
        self.display2.fill(color565(0, 0, 0))
        self.display2.text(vga1_bold_16x32, "Vader is coming!", 0, 100, color565(255, 0, 0), color565(0, 0, 0))
        # self.animate_title_start = ticks_ms()

        print("Playing Imperial March")
        self.play_song()
        # self.display.fill(color565(0, 0, 0))
        # self.display2.fill(color565(0, 0, 0))

    # async def update(self):
    #     self.animate_title()
    #     await asyncio.sleep(0.033)

    def display_center_text(self, text):
        # Get dimensions and font size
        width = self.display.width()
        height = self.display.height()
        text_width = len(text) * 16  # 16px per character
        text_height = 32  # Font height
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        self.display.text(vga1_bold_16x32, text, x, y, color565(255, 255, 255), color565(0, 0, 0))

    # def animate_title(self):
    #     elapsed = ticks_diff(ticks_ms(), self.animate_title_start) // 100
    #     pulse = int((1 + math.sin(elapsed * 0.2)) * 127.5)
    #     red = max(0, min(255, pulse))
    #     color = color565(red, 0, 0)
    #     self.display.fill(color565(0, 0, 0))
    #     self.display.text(vga1_bold_16x32, "Imperial March", 10, 100, color, color565(0, 0, 0))

    def flash_leds(self, duration_ms):
        dim_red = (51, 0, 0)
        dim_blue = (0, 0, 51)
        color = dim_red if self.counter % 2 == 0 else dim_blue
        for i in range(7):
            self.leds[i] = color
        self.leds.write()
        sleep(duration_ms / 1000)
        for i in range(7):
            self.leds[i] = (0, 0, 0)
        self.leds.write()

    def beep(self, note, duration_ms):
        freq = note
        if freq > 0:
            pwm = PWM(self.pin_piezo, freq=freq, duty=512)
            self.flash_leds(duration_ms)
            pwm.deinit()
        else:
            sleep(duration_ms / 1000)
        sleep(0.05)
        self.counter += 1

    def first_section(self):
        for n, d in [
            (440, 500), (440, 500), (440, 500), (349, 350), (523, 150), (440, 500),
            (349, 350), (523, 150), (440, 650), (659, 500), (659, 500), (659, 500),
            (698, 350), (523, 150), (415, 500), (349, 350), (554, 150), (440, 650)
        ]:
            # self.animate_title()
            self.beep(n, d)
        sleep(0.5)

    def second_section(self):
        for n, d in [
            (880, 500), (440, 300), (440, 150), (880, 500), (830, 325), (784, 175),
            (740, 125), (698, 125), (740, 250), (455, 250), (622, 500),
            (587, 325), (554, 175), (523, 125), (466, 125), (523, 250)
        ]:
            # self.animate_title()
            self.beep(n, d)
        sleep(0.35)

    def play_song(self):
        # self.controller.bsp.speaker.start_song("imperial_march")
        print("Started Imperial March song")
        self.first_section()
        self.second_section()

        for n, d in [
            (349, 250), (415, 500), (349, 350), (440, 125), (523, 500),
            (440, 375), (523, 125), (659, 650)
        ]:
            # self.animate_title()
            self.beep(n, d)

        sleep(0.5)
        self.second_section()

        for n, d in [
            (349, 250), (415, 500), (349, 375), (523, 125), (440, 500),
            (349, 375), (523, 125), (440, 650)
        ]:
            # self.animate_title()
            self.beep(n, d)

        sleep(0.65)

if __name__ == "__main__":
    from single_app_runner import run_app
    run_app(ImperialMarch)