import asyncio
from apps.app import BaseApp
from machine import Pin, PWM
import gc9a01
import vga1_bold_16x32
import neopixel

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
        self.pwm = None
        self.task = None

        self.display.fill(gc9a01.BLACK)
        self.task = asyncio.create_task(self.display_center_text("Imperial March ", self.display))
        self.display2.fill(gc9a01.BLACK)
        self.task = asyncio.create_task(self.display_center_text("Vader is coming!", self.display2))

        print("Playing Imperial March")
        self.task = asyncio.create_task(self.play_song())

    async def display_center_text(self, text, screen):
        # Get dimensions and font size
        width = self.display.width()
        height = self.display.height()
        text_width = len(text) * 15 # 15px per character
        text_height = 32  # Font height
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        screen.text(vga1_bold_16x32, text, x, y, gc9a01.RED , gc9a01.BLACK)

    async def flash_leds(self, duration_ms):
        dim_red = (51, 0, 0)
        dim_blue = (0, 0, 51)
        color = dim_red if self.counter % 2 == 0 else dim_blue
        for i in range(7):
            self.leds[i] = color
        self.leds.write()
        await asyncio.sleep(duration_ms / 1000)
        for i in range(7):
            self.leds[i] = (0, 0, 0)
        self.leds.write()

    async def beep(self, note, duration_ms):
        freq = note
        if freq > 0:
            self.pwm = PWM(self.pin_piezo, freq=freq, duty=512)
            await self.flash_leds(duration_ms)
            self.pwm.deinit()
        else:
            await asyncio.sleep(duration_ms / 1000)
        await asyncio.sleep(0.05)
        self.counter += 1

    async def first_section(self):
        for n, d in [
            (440, 500), (440, 500), (440, 500), (349, 350), (523, 150), (440, 500),
            (349, 350), (523, 150), (440, 650), (659, 500), (659, 500), (659, 500),
            (698, 350), (523, 150), (415, 500), (349, 350), (554, 150), (440, 650)
        ]:
            await self.beep(n, d)
        await asyncio.sleep(0.5)

    async def second_section(self):
        for n, d in [
            (880, 500), (440, 300), (440, 150), (880, 500), (830, 325), (784, 175),
            (740, 125), (698, 125), (740, 250), (455, 250), (622, 500),
            (587, 325), (554, 175), (523, 125), (466, 125), (523, 250)
        ]:
            await self.beep(n, d)
        await asyncio.sleep(0.35)

    async def play_song(self):
        print("Started Imperial March song")
        await self.first_section()
        await self.second_section()

        for n, d in [
            (349, 250), (415, 500), (349, 350), (440, 125), (523, 500),
            (440, 375), (523, 125), (659, 650)
        ]:
            await self.beep(n, d)

        await asyncio.sleep(0.5)
        await self.second_section()

        for n, d in [
            (349, 250), (415, 500), (349, 375), (523, 125), (440, 500),
            (349, 375), (523, 125), (440, 650)
        ]:
            await self.beep(n, d)

        await asyncio.sleep(0.65)

    async def teardown(self):
        if self.pwm:
            self.pwm.deinit()
        if self.task:
            self.task.cancel()
        self.controller.neopixel.fill((0, 0, 0))
        self.controller.neopixel.write()

if __name__ == "__main__":
    from single_app_runner import run_app
    run_app(ImperialMarch)