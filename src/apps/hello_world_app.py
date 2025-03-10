from apps import BaseApp

class HelloWorld(BaseApp):
    def __init__(self, controller):
        super().__init__(controller)

        # This would be an automatically instantiated property in the base class 
        # based on some global singleton function...
        self.controller.bsp.displays.display_center_text(
            "Hello, World!"
        )

