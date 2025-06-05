import apps.app

class App(apps.app.BaseApp):
    hidden = True
    def __init__(self, controller):
        super().__init__(controller)
        displays = self.controller.bsp.displays
        white = displays.COLOR_LOOKUP['white']
        displays.display1.fill(white)
        displays.display2.fill(white)
