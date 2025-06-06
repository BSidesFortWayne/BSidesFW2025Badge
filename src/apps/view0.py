# Home

import asyncio
import gc9a01
from apps.app import BaseApp
import fonts.arial32px as arial32px
from lib.smart_config import ColorConfig

class App(BaseApp):
    """
    Displays name on both screens.
    The buttons go to the other 4 views.
    """
    name = "Badge"
    def __init__(self, controller):
        super().__init__(controller)
        self.view = 0
        displays = self.controller.bsp.displays
        self.config.add('first_name', 'WhatAbout')
        self.config.add('last_name', 'Bob')
        self.config.add('company', 'BSidesFW')
        self.config.add('title', '2025')
        self.config.add('background_image', "img/bsides_logo.jpg")
        self.config.add('fg_color', ColorConfig('FG Color', displays.COLOR_LOOKUP['gc9a01']['white']))
        self.config.add('bg_color', ColorConfig('FG Color', displays.COLOR_LOOKUP['gc9a01']['black']))

        self.last_checksum = self.config.checksum()

    def wrap_text(self, text, font, max_width, display):
        words = text.split(' ')
        lines = []
        current_line = ''

        for word in words:
            if display.write_len(font, current_line + word + ' ') <= max_width:
                current_line += word + ' '
            else:
                lines.append(current_line.strip())
                current_line = word + ' '
        if current_line:
            lines.append(current_line.strip())
        return lines

    async def setup(self):
        first_name = self.config['first_name']
        last_name = self.config['last_name']
        company = self.config['company']
        title = self.config['title']
        image = self.config['background_image']
        displays = self.controller.bsp.displays
        white = displays.COLOR_LOOKUP['gc9a01']['white']
        black = displays.COLOR_LOOKUP['gc9a01']['black']

        if not first_name and not last_name:
            displays.display_center_text(
                'NO',
                white,
                black,
                1,
                arial32px
            )
            displays.display_center_text(
                'NAME',
                white,
                black,
                2,
                arial32px
            )
        else:
            # Convert hex to RGB
            display1_fg_color = self.config['fg_color'].value()
            display2_fg_color = self.config['fg_color'].value()
            display1_bg_color = self.config['bg_color'].value()
            display2_bg_color = self.config['bg_color'].value()

            # if 'background_image' not in self.config:
            #     displays.display1.fill(display1_bg_color)
            #     displays.display2.fill(display2_bg_color)
            # else:
            #     displays[0].jpg(image, 0, 0, gc9a01.FAST)
            #     displays[1].jpg(image, 0, 0, gc9a01.FAST)

            displays.display1.fill(display1_bg_color)
            displays.display2.fill(display2_bg_color)

            max_width = displays.display1.width() - 40  # Adjust padding as needed
            wrapped_first_name = self.wrap_text(first_name, arial32px, max_width, displays.display1)
            wrapped_last_name = self.wrap_text(last_name, arial32px, max_width, displays.display1)
            wrapped_company = self.wrap_text(company, arial32px, max_width, displays.display2)
            wrapped_title = self.wrap_text(title, arial32px, max_width, displays.display2)

            # Debugging information
            print("Wrapped First Name:", wrapped_first_name)
            print("Wrapped Last Name:", wrapped_last_name)
            print("Wrapped Company:", wrapped_company)
            print("Wrapped Title:", wrapped_title)

            # Calculate total height of the wrapped text
            total_height_first_name = len(wrapped_first_name) * arial32px.HEIGHT
            total_height_last_name = len(wrapped_last_name) * arial32px.HEIGHT
            total_height_company = len(wrapped_company) * arial32px.HEIGHT
            total_height_title = len(wrapped_title) * arial32px.HEIGHT

            # Move veritical alignment up by X pixels
            adjustment = 10

            # Calculate y-offset to center the text vertically
            y_offset_first_name = (displays.display1.height() - total_height_first_name) // 2 - adjustment
            y_offset_last_name = (displays.display1.height() - total_height_last_name) // 2 - adjustment
            y_offset_company = (displays.display2.height() - total_height_company) // 2 - adjustment
            y_offset_title = (displays.display2.height() - total_height_title) // 2 - adjustment

            # Render first name and last name on display1
            for i, line in enumerate(wrapped_first_name):
                displays.display1.write(
                    arial32px,
                    line,
                    int((displays.display1.width() / 2) - (displays.display1.write_len(arial32px, line) / 2)),
                    y_offset_first_name + i * arial32px.HEIGHT,
                    white,
                    black
                )

            for i, line in enumerate(wrapped_last_name):
                displays.display1.write(
                    arial32px,
                    line,
                    int((displays.display1.width() / 2) - (displays.display1.write_len(arial32px, line) / 2)),
                    y_offset_last_name + i * arial32px.HEIGHT + total_height_first_name,
                    white,
                    black
                )

            # Render company and title on display2
            for i, line in enumerate(wrapped_company):
                displays.display2.write(
                    arial32px,
                    line,
                    int((displays.display2.width() / 2) - (displays.display2.write_len(arial32px, line) / 2)),
                    y_offset_company + i * arial32px.HEIGHT,
                    white,
                    black
                )

            for i, line in enumerate(wrapped_title):
                displays.display2.write(
                    arial32px,
                    line,
                    int((displays.display2.width() / 2) - (displays.display2.write_len(arial32px, line) / 2)),
                    y_offset_title + i * arial32px.HEIGHT + total_height_company,
                    white,
                    black
                )

    async def update(self):
        if self.config.checksum() != self.last_checksum:
            await self.setup()
            self.last_checksum = self.config.checksum()

        await asyncio.sleep(3)