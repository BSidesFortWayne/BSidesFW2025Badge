# Home

import apps.view
import fonts.arial32px as arial32px
import fonts.arial16px as arial16px
from machine import Pin, ADC # type: ignore

class View(apps.view.View):
    """
    Displays name on both screens.
    The buttons go to the other 4 views.
    """

    def __init__(self, views):
        self.view = 0
        self.views = views
        if self.views.name == None:
            self.views.displays.display_center_write(
                'NO',
                self.views.displays.gc9a01.WHITE,
                self.views.displays.gc9a01.BLACK,
                1,
                arial32px
            )
            self.views.displays.display_center_write(
                'NAME',
                self.views.displays.gc9a01.WHITE,
                self.views.displays.gc9a01.BLACK,
                2,
                arial32px
            )
        else:
            # Convert hex to RGB
            display1_fg_color = tuple(int(self.views.name['fg_color'][0].replace('#', '')[i:i+2], 16) for i in (0, 2, 4))
            display1_fg_color = tuple(int(self.views.name['fg_color'][1].replace('#', '')[i:i+2], 16) for i in (0, 2, 4))
            display1_bg_color = tuple(int(self.views.name['bg_color'][0].replace('#', '')[i:i+2], 16) for i in (0, 2, 4))
            display2_bg_color = tuple(int(self.views.name['bg_color'][1].replace('#', '')[i:i+2], 16) for i in (0, 2, 4))

            if not 'background_image' in self.views.name:
                self.views.displays.display1.fill(self.views.displays.gc9a01.color565(display1_bg_color[0], display1_bg_color[1], display1_bg_color[2]))
                self.views.displays.display2.fill(self.views.displays.gc9a01.color565(display2_bg_color[0], display2_bg_color[1], display2_bg_color[2]))
            else:
                self.views.displays.display1.jpg(self.views.name['background_image'][0], 0, 0, self.views.displays.gc9a01.FAST)
                self.views.displays.display2.jpg(self.views.name['background_image'][1], 0, 0, self.views.displays.gc9a01.FAST)

            self.views.displays.display1.write(
                arial32px,
                self.views.name['first'],
                int((self.views.displays.display1.width()/2) - ((self.views.displays.display1.write_len(arial32px, self.views.name['first'])/2))),
                int((self.views.displays.display1.height()/2) - arial32px.HEIGHT),
                self.views.displays.gc9a01.WHITE,
                self.views.displays.gc9a01.BLACK
            )
            self.views.displays.display1.write(
                arial32px,
                self.views.name['last'],
                int((self.views.displays.display1.width()/2) - ((self.views.displays.display1.write_len(arial32px, self.views.name['last'])/2))),
                int((self.views.displays.display1.height()/2)),
                self.views.displays.gc9a01.WHITE,
                self.views.displays.gc9a01.BLACK
            )

            self.views.displays.display2.write(
                arial32px,
                self.views.name['company'],
                int((self.views.displays.display2.width()/2) - ((self.views.displays.display2.write_len(arial32px, self.views.name['company'])/2))),
                int((self.views.displays.display2.height()/2) - arial32px.HEIGHT),
                self.views.displays.gc9a01.WHITE,
                self.views.displays.gc9a01.BLACK
            )
            self.views.displays.display2.write(
                arial32px,
                self.views.name['title'],
                int((self.views.displays.display2.width()/2) - ((self.views.displays.display2.write_len(arial32px, self.views.name['title'])/2))),
                int((self.views.displays.display2.height()/2)),
                self.views.displays.gc9a01.WHITE,
                self.views.displays.gc9a01.BLACK
            )

    def button_press(self, button):
        view_mapping = [1, 6, 5, 4]
        if button in view_mapping:
            self.views.switch_view(view_mapping.index(button)+1)
