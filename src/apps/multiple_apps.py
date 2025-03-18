from apps.app import BaseApp

"""
This file demonstrates how to create multiple apps in a single file.

This is helpful if you want to develop multiple apps in a single file and share code 
between them. It also helps to keep the code organized and maintainable.
"""
class HelloWorld1(BaseApp):
    name = "Hello World 1"
    version = "0.0.2"
    def __init__(self, controller):
        super().__init__(controller)

        # This would be an automatically instantiated property in the base class 
        # based on some global singleton function...
        self.controller.bsp.displays.display_center_text(
            "Hello, World, app 1"
        )


class HelloWorld2(BaseApp):
    name = "Hello World 2"
    version = "0.0.2"
    def __init__(self, controller):
        super().__init__(controller)

        # This would be an automatically instantiated property in the base class 
        # based on some global singleton function...
        self.controller.bsp.displays.display_center_text(
            "Hello, World, app 2"
        )
