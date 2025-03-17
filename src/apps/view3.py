import apps.app

class App(apps.app.BaseApp):
    def __init__(self, controller):
        super().__init__(controller, "View 3")
        self.controller.displays.display1.fill(self.controller.displays.gc9a01.BLUE)
        self.controller.displays.display2.fill(self.controller.displays.gc9a01.BLUE)

    def button_press(self, button):
        if button == 1:
            # Back to home
            self.controller.switch_view(0)
