from apps.app import BaseApp
import gc9a01 
import math
from machine import RTC 

import framebuf

import fonts.arial16px as arial16px
from lib.smart_config import BoolDropdownConfig, ColorConfig, EnumConfig


FULL_REDRAW = 0
PARTIAL_REDRAW = 1
FULL_REDRAW_FB = 2
PARTIAL_REDRAW_FB = 3

class AnalogClock(BaseApp):
    name = "Analog Clock"
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.display1 = self.controller.bsp.displays.display1

        print("Pre-config Analog Clock")

        bg_range = self.config.add('bg_color', ColorConfig('BG Color', gc9a01.WHITE), force=True)
        fg_range = self.config.add('fg_color', ColorConfig('FG Color', gc9a01.BLACK), force=True)
        self.config.add('hours_hand_color', ColorConfig('Hours Hand Color', gc9a01.BLACK), force=True)
        self.config.add('minutes_hand_color', ColorConfig('Minutes Hand Color', gc9a01.BLACK), force=True)
        self.config.add('seconds_hand_color', ColorConfig('Seconds Hand Color', gc9a01.RED), force=True)
        self.config.add(
            'draw method', 
            EnumConfig(
                'draw method', 
                [
                    'full redraw', 
                    'partial redraw'
                ],
                'full redraw'
            ),
            force=True
        )
        
        radius = self.config.add('radius', 110)

        use_frame_buffer = self.config.add(
            'use frame buffer',
            BoolDropdownConfig('use frame buffer', True),
            force=True
        ).value()

        print("Post-config Analog Clock")

        self.last_second = 0

        self.font = arial16px

        self.center = self.display1.width() // 2

        self.rtc = RTC()

        self.rtc.datetime((2025, 3, 8, 6, 9, 18, 50, 0))

        self.mem_buf = bytearray(240*240*3)
        self.fbuf = framebuf.FrameBuffer(
            self.mem_buf, 
            240, 
            240, 
            framebuf.RGB565
        )

        if use_frame_buffer:
            self.draw_clock_face_fb(bg_range.value(), fg_range.value(), radius)
        else:
            self.draw_clock_face(bg_range.value(), fg_range.value(), radius)
            


    def draw_clock_face_fb(self, bg_color: int, fg_color: int, radius: int):
        self.fbuf.fill(bg_color)

        # clock border
        self.fbuf.ellipse(
            self.center, 
            self.center, 
            radius, 
            radius, 
            fg_color,
            False
        )

        # center dot for arms
        self.fbuf.ellipse(
            self.center,
            self.center,
            2,
            2,
            fg_color,
            True
        )

        # Draw the clock numbers
        for i in range(1, 13):
            angle = (30 * i - 90) * math.pi / 180
            offset = radius - 20
            x = self.center + int(offset * math.cos(angle))
            y = self.center + int(offset * math.sin(angle))
            self.fbuf.text(str(i), x - 4, y - 8, fg_color)
        
        # Draw the clock ticks
        for i in range(0, 60):
            angle = (6 * i - 90) * math.pi / 180
            offsetStart = radius - 10
            offsetEnd = radius
            x = self.center + int(offsetStart * math.cos(angle))
            y = self.center + int(offsetStart * math.sin(angle))
            x2 = self.center + int(offsetEnd * math.cos(angle))
            y2 = self.center + int(offsetEnd * math.sin(angle))
            self.fbuf.line(x, y, x2, y2, fg_color)

    def draw_clock_face(self, bg_color: int, fg_color: int, radius: int):
        self.display1.fill(bg_color)

        # clock border
        self.display1.circle(self.center, self.center, radius, fg_color)

        # center dot for arms
        self.display1.circle(self.center, self.center, 2, fg_color)

        # Draw the clock numbers
        for i in range(1, 13):
            angle = (30 * i - 90) * math.pi / 180
            # PEMDAS
            offset = radius - 20
            x = self.center + int(offset * math.cos(angle))
            y = self.center + int(offset * math.sin(angle))
            # self.display1.fill_circle(x, y, 5, gc9a01.BLACK)
            self.display1.write(self.font, str(i), x - 4, y - 8, fg_color, bg_color)
        
        # Draw the clock ticks
        for i in range(0, 60):
            angle = (6 * i - 90) * math.pi / 180
            offsetStart = radius - 10
            offsetEnd = radius
            x = self.center + int(offsetStart * math.cos(angle))
            y = self.center + int(offsetStart * math.sin(angle))
            x2 = self.center + int(offsetEnd * math.cos(angle))
            y2 = self.center + int(offsetEnd * math.sin(angle))
            self.display1.line(x, y, x2, y2, fg_color)


    def draw_time_hand_fb(self, angle: float, length: int, color: int):
        x = self.center + int(length * math.cos(angle))
        y = self.center + int(length * math.sin(angle))
        self.fbuf.line(self.center, self.center, x, y, color)

    def draw_hour_hand_fb(self, hour: float, color: int, radius: int):
        angle = (30 * hour - 90) * math.pi / 180
        self.draw_time_hand_fb(angle, radius - 50, color)

    def draw_minute_hand_fb(self, minute: float, color: int, radius: int):
        angle = (6 * minute - 90) * math.pi / 180
        self.draw_time_hand_fb(angle, radius - 30, color)

    def draw_second_hand_fb(self, second: float, color: int, radius: int):
        angle = (6 * second - 90) * math.pi / 180
        self.draw_time_hand_fb(angle, radius - 30, color)
    
    def draw_time_hand(self, angle: float, length: int, color: int):
        x = self.center + int(length * math.cos(angle))
        y = self.center + int(length * math.sin(angle))
        self.display1.line(self.center, self.center, x, y, color)

    def draw_hour_hand(self, hour: float, color: int, radius: int):
        angle = (30 * hour - 90) * math.pi / 180
        self.draw_time_hand(angle, radius - 50, color)
    
    def draw_minute_hand(self, minute: float, color: int, radius: int):
        angle = (6 * minute - 90) * math.pi / 180
        self.draw_time_hand(angle, radius - 30, color)
    
    def draw_second_hand(self, second: float, color: int, radius: int):
        angle = (6 * second - 90) * math.pi / 180
        self.draw_time_hand(angle, radius - 30, color)

    async def update(self):
        datetime = self.rtc.datetime()
        radius = self.config['radius']
        bg_color = self.config['bg_color'].value()
        fg_color = self.config['fg_color'].value()
        use_frame_buffer = self.config['use frame buffer'].value()
        use_partial_redraw = self.config['draw method'].value() != 'full redraw'
        
        # Get hours, minutes, and seconds from ms timestamp. Don't use datetime
        # because it's not accurate enough.
        year, month, day, weekday, hour, minute, second, ms = datetime

        if use_frame_buffer:
            self.draw_clock_face_fb(bg_color, fg_color, radius)
        elif not use_partial_redraw:
            # Draw the whole face if not using the partial method
            self.draw_clock_face(bg_color, fg_color, radius)
        else:
            # erase previous hands in the 'partial' implementation
            if second != self.last_second:
                self.draw_hour_hand(hour, bg_color, radius)
                self.draw_hour_hand(hour-1, bg_color, radius)
                self.draw_minute_hand(minute-1, bg_color, radius)
                self.draw_second_hand(second-1, bg_color, radius)

        # draw new hands
        # it would be neat to make the hours angle fractional based on the minutes
        # but this would need to update the previous hand delete logic
        # TODO add partial FB redraw logic for faster drawing
        if use_frame_buffer:
            self.draw_hour_hand_fb(hour + (minute / 60), self.config['hours_hand_color'].value(), radius)
            self.draw_minute_hand_fb(minute + (second / 60), self.config['minutes_hand_color'].value(), radius)

            # draw seconds hand with fractional milliseconds
            # milliseconds vlaue can be 1-6 digits so that needds
            # to be accounte for as well
            self.draw_second_hand_fb(second + (ms / 1_000_000), self.config['seconds_hand_color'].value(), radius)
            
            self.display1.blit_buffer(
                self.mem_buf,
                0,
                0,
                240,
                240
            )
        else:
            self.draw_hour_hand(hour, self.config['hours_hand_color'].value(), radius)
            self.draw_minute_hand(minute, self.config['minutes_hand_color'].value(), radius)
            self.draw_second_hand(second, self.config['seconds_hand_color'].value(), radius)

        self.last_second = second
        
