import apps.app

class App(apps.app.BaseApp):
    name = "Blue View"
    def __init__(self, controller):
        super().__init__(controller)
        displays = self.controller.bsp.displays
        blue = displays.COLOR_LOOKUP['blue']
        displays.display1.fill(blue)
        displays.display2.fill(blue)

