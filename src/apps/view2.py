import apps.app
import gc9a01

class App(apps.app.BaseApp):
    name = "Green View"
    def __init__(self, controller: apps.app.IController):
        self.view = 2
        self.views = controller
        self.views.displays.display1.fill(gc9a01.GREEN)
        self.views.displays.display2.fill(gc9a01.GREEN)
        