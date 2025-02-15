# Home

import views.view
import vga1_bold_16x32 as font

class View(views.view.View):
    """
    Displays name on both screens.
    The buttons go to the other 4 views.
    """

    def __init__(self, views):
        self.views = views
        self.views.displays.display1.fill(self.views.displays.gc9a01.BLUE)
        self.views.displays.display2.fill(self.views.displays.gc9a01.BLUE)
        self.views.displays.display_center_text(font, self.views.name['first'], self.views.displays.display1, self.views.displays.gc9a01.RED, self.views.displays.gc9a01.BLUE)
        self.views.displays.display_center_text(font, self.views.name['last'], self.views.displays.display2, self.views.displays.gc9a01.RED, self.views.displays.gc9a01.BLUE)

    def button_press(self, button):
        self.views.switch_view(button)
