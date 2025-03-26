import gc9a01
from apps.app import BaseApp

class App(BaseApp):
    # This will be the name of the app that is displayed in the app menu
    name = "Hello World"

    # This will be the version of the app that is displayed in the app menu
    version = "0.0.2"
    
    def __init__(self, controller):
        super().__init__(controller)

        # This would be an automatically instantiated property in the base class 
        # based on some global singleton function...
        self.controller.bsp.displays.display1.fill(gc9a01.BLACK)
        self.controller.bsp.displays.display_center_text(
            "Hello, World!"
        )

