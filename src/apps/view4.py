import apps.app

class App(apps.app.BaseApp):
    def __init__(self, controller):
        super().__init__(controller, "View 4")
        self.view = 4
        self.views = controller
        self.views.displays.display1.fill(self.views.displays.gc9a01.WHITE)
        self.views.displays.display2.fill(self.views.displays.gc9a01.WHITE)

    def button_press(self, button):
        if button == 1:
            # Back to home
            self.views.switch_view(0)
