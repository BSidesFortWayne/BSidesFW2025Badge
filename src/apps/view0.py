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

    async def setup(self):
        first_name = self.config['first_name']
        last_name = self.config['last_name']
        company = self.config['company']
        title = self.config['title']
        image = self.config['background_image']
        displays = self.controller.bsp.displays
        # if there is a space in the name, split it
        white = displays.COLOR_LOOKUP['gc9a01']['white']
        black = displays.COLOR_LOOKUP['gc9a01']['black']
        # if there is a space in the name, split it
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
            # display1_fg_color = tuple(int(self.config['fg_color'][0].replace('#', '')[i:i+2], 16) for i in (0, 2, 4))
            # display2_fg_color = tuple(int(self.config['fg_color'][1].replace('#', '')[i:i+2], 16) for i in (0, 2, 4))
            # display1_bg_color = tuple(int(self.config['bg_color'][0].replace('#', '')[i:i+2], 16) for i in (0, 2, 4))
            # display2_bg_color = tuple(int(self.config['bg_color'][1].replace('#', '')[i:i+2], 16) for i in (0, 2, 4))

            if 'background_image' not in self.config:
                displays.display1.fill(display1_bg_color)
                displays.display2.fill(display1_bg_color)
            else:
                displays[0].jpg(image, 0, 0, gc9a01.FAST)
                displays[1].jpg(image, 0, 0, gc9a01.FAST)

            displays.display1.write(
                arial32px,
                first_name,
                int((displays.display1.width()/2) - ((displays.display1.write_len(arial32px, first_name)/2))),
                int((displays.display1.height()/2) - arial32px.HEIGHT),
                white,
                black
            )
            displays.display1.write(
                arial32px,
                last_name,
                int((displays.display1.width()/2) - ((displays.display1.write_len(arial32px, last_name)/2))),
                int((displays.display1.height()/2)),
                white,
                black,
            )

            displays.display2.write(
                arial32px,
                company,
                int((displays.display2.width()/2) - ((displays.display2.write_len(arial32px, company)/2))),
                int((displays.display2.height()/2) - arial32px.HEIGHT),
                white,
                black
            )
            displays.display2.write(
                arial32px,
                title,
                int((displays.display2.width()/2) - ((displays.display2.write_len(arial32px, title)/2))),
                int((displays.display2.height()/2)),
                white,
                black
            )

    async def update(self):
        if self.config.checksum() != self.last_checksum:
            await self.setup()
            self.last_checksum = self.config.checksum()
        
        await asyncio.sleep(3)