import asyncio
import time
from apps.app import BaseApp
import framebuf

def rgb(color: tuple):
    r,g,b = color
    return (r & 0xF8) | ((g & 0xE0) >> 5) | ((g & 0x1C) << 11) | ((b & 0xF8) << 5)

class ButtonFidget(BaseApp):
    name = "Button Fidget"

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.display = self.controller.bsp.displays.display1
        self.counter = 0
        self.fbuf_mem = bytearray(240 * 240 * 2)
        self.fbuf_width = 240
        self.fbuf_height = 240
        self.fbuf_mv = memoryview(self.fbuf_mem)
        self.fbuf = framebuf.FrameBuffer(
            self.fbuf_mv,
            self.fbuf_width,
            self.fbuf_height,
            framebuf.RGB565
        )

        self.buttons = self.controller.bsp.buttons

        self.indicator_width = 20
        self.indicator_height = 20
        self.padding = 5
        total_width = self.indicator_width * len(self.buttons) + self.padding * (len(self.buttons) - 1)
        total_height = self.indicator_height * 3 + self.padding * 2
        self.offset_x = (self.fbuf_width - total_width) // 2
        self.offset_y = (self.fbuf_height - total_height) // 2
        self.offset_y -= 20

        self.text_offset = 20
        self.start_time = 0

        self.leds = self.controller.bsp.leds

        self.released_color = (255, 0, 0)
        self.pressed_color = (0, 255, 0)
        self.long_pressed_color = (0, 0, 255)

        self.state_to_color = {
            "Released": self.released_color,
            "Pressed": self.pressed_color,
            "Long Pressed": self.long_pressed_color,
        }


    async def update(self):
        fbuf = self.fbuf
        # gen_start = time.ticks_ms()
        fbuf.fill(0x0000)

        leds = self.leds
        state_to_color = self.state_to_color

        offset_x = self.offset_x
        offset_y = self.offset_y

        released_color = self.released_color
        pressed_color = self.pressed_color
        long_pressed_color = self.long_pressed_color
        
        indicator_height = self.indicator_height
        indicator_width = self.indicator_width
        padding = self.padding
        text_offset = self.text_offset
        buttons = self.buttons

        y = offset_y
        y_increment = indicator_height + padding
        
        # Draw first column with text for each button
        fbuf.text("B",  offset_x - text_offset, y, 0xFFFF)
        fbuf.text("LP", offset_x - text_offset, y+y_increment + 6, 0xFFFF)
        fbuf.text("P",  offset_x - text_offset, y+y_increment*2 + 6, 0xFFFF)
        fbuf.text("R",  offset_x - text_offset, y+y_increment*3 + 6, 0xFFFF)        

        any_pressed = False
        for i,state in enumerate(buttons):
            # Check if any button is pressed
            if state == "Pressed" or state == "Long Pressed":
                any_pressed = True

            x = offset_x + i * (indicator_width + padding)

            # Draw button number as column header
            fbuf.text(str(i), x + 5, y, 0xFFFF)

            leds.set_led_color(i, state_to_color[state])
            
            # Draw first row as a circle and fill if "Long Pressed"\
            method = fbuf.fill_rect if state == "Long Pressed" else fbuf.rect
            method(
                x, 
                y+y_increment, 
                indicator_width, 
                indicator_height, 
                rgb(long_pressed_color)
            )

            # Draw second row as a circle and fill if "Pressed" or "Long Pressed"
            method = fbuf.fill_rect if state == "Pressed" else fbuf.rect
            method(
                x, 
                y+y_increment*2, 
                indicator_width, 
                indicator_height, 
                rgb(pressed_color)
            )

            # Draw third row as a circle and fill if "Released"
            method = fbuf.fill_rect if state == "Released" else fbuf.rect
            method(
                x, 
                y+y_increment*3, 
                indicator_width, 
                indicator_height, 
                rgb(released_color)
            )
        
        if any_pressed:
            if not self.start_time:
                self.start_time = time.ticks_ms()
            elapsed = time.ticks_diff(time.ticks_ms(), self.start_time)
            fbuf.text(
                f"Elapsed: {round(elapsed / 1000, 1)} s",
                offset_x,
                offset_y - text_offset,
                0xFFFF
            )
        else:
            self.start_time = 0
    
        gen_end = time.ticks_ms()
        
        self.controller.bsp.displays.display1.blit_buffer(
            self.fbuf_mv,
            x,
            y,
            self.fbuf_width,
            self.fbuf_height,
        )

        self.controller.bsp.displays.display1.blit_buffer(
            self.fbuf_mv,
            0,
            0,
            self.fbuf_width,
            self.fbuf_height,
        )

        # frame_count += 1
        # if frame_count % 100 == 0:
        #     time_end = time.ticks_ms()
        #     diff_s = (time_end - time_start) / 1000
        #     total_frames = frame_count - last_frame_count
        #     print(f'{total_frames / diff_s} FPS')
        #     time_start = time.ticks_ms()
        #     last_frame_count = frame_count


if __name__ == "__main__":
    from single_app_runner import run_app
    run_app(ButtonFidget)