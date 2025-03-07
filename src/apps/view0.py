# Home

import apps.view

class View(apps.view.View):
    """
    Displays name on both screens.
    The buttons go to the other 4 views.
    """

    def __init__(self, controller):
        print("view0 init")
        self.controller = controller
        self.controller.displays.display1.fill(0x0000FF)
        self.controller.displays.display2.fill(0x00FF00)
        self.controller.displays.display_center_text(self.controller.name['first'], 0x0000FF, 0x00FF00, 1)
        self.controller.displays.display_center_text(self.controller.name['last'], 0x00FF00, 0x0000FF, 2)
    
    def button_press(self, button):
        print("view0 button_press")
        self.controller.switch_view(button)
