# Home

from apps.app import BaseApp
import fonts.arial32px as arial32px

class App(BaseApp):
    """
    Displays name on both screens.
    The buttons go to the other 4 views.
    """

    def __init__(self, controller):
        super().__init__(controller, "Badge")
        self.view = 0
        if not self.controller.name:
            self.controller.displays.display_center_write(
                'NO',
                self.controller.displays.gc9a01.WHITE,
                self.controller.displays.gc9a01.BLACK,
                1,
                arial32px
            )
            self.controller.displays.display_center_write(
                'NAME',
                self.controller.displays.gc9a01.WHITE,
                self.controller.displays.gc9a01.BLACK,
                2,
                arial32px
            )
        else:
            # Convert hex to RGB
            display1_fg_color = tuple(int(self.controller.name['fg_color'][0].replace('#', '')[i:i+2], 16) for i in (0, 2, 4))
            display2_fg_color = tuple(int(self.controller.name['fg_color'][1].replace('#', '')[i:i+2], 16) for i in (0, 2, 4))
            display1_bg_color = tuple(int(self.controller.name['bg_color'][0].replace('#', '')[i:i+2], 16) for i in (0, 2, 4))
            display2_bg_color = tuple(int(self.controller.name['bg_color'][1].replace('#', '')[i:i+2], 16) for i in (0, 2, 4))

            if 'background_image' not in self.controller.name:
                self.controller.displays.display1.fill(self.controller.displays.gc9a01.color565(display1_bg_color[0], display1_bg_color[1], display1_bg_color[2]))
                self.controller.displays.display2.fill(self.controller.displays.gc9a01.color565(display2_bg_color[0], display2_bg_color[1], display2_bg_color[2]))
            else:
                self.controller.displays.display1.jpg(self.controller.name['background_image'][0], 0, 0, self.controller.displays.gc9a01.FAST)
                self.controller.displays.display2.jpg(self.controller.name['background_image'][1], 0, 0, self.controller.displays.gc9a01.FAST)

            self.controller.displays.display1.write(
                arial32px,
                self.controller.name['first'],
                int((self.controller.displays.display1.width()/2) - ((self.controller.displays.display1.write_len(arial32px, self.controller.name['first'])/2))),
                int((self.controller.displays.display1.height()/2) - arial32px.HEIGHT),
                self.controller.displays.gc9a01.WHITE,
                self.controller.displays.gc9a01.BLACK
            )
            self.controller.displays.display1.write(
                arial32px,
                self.controller.name['last'],
                int((self.controller.displays.display1.width()/2) - ((self.controller.displays.display1.write_len(arial32px, self.controller.name['last'])/2))),
                int((self.controller.displays.display1.height()/2)),
                self.controller.displays.gc9a01.WHITE,
                self.controller.displays.gc9a01.BLACK
            )

            self.controller.displays.display2.write(
                arial32px,
                self.controller.name['company'],
                int((self.controller.displays.display2.width()/2) - ((self.controller.displays.display2.write_len(arial32px, self.controller.name['company'])/2))),
                int((self.controller.displays.display2.height()/2) - arial32px.HEIGHT),
                self.controller.displays.gc9a01.WHITE,
                self.controller.displays.gc9a01.BLACK
            )
            self.controller.displays.display2.write(
                arial32px,
                self.controller.name['title'],
                int((self.controller.displays.display2.width()/2) - ((self.controller.displays.display2.write_len(arial32px, self.controller.name['title'])/2))),
                int((self.controller.displays.display2.height()/2)),
                self.controller.displays.gc9a01.WHITE,
                self.controller.displays.gc9a01.BLACK
            )

    def button_press(self, button):
        # view_mapping = [1, 6, 5, 4]
        # if button in view_mapping:
        self.controller.switch_view(button)


print("Badge loaded")