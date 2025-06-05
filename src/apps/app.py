from lib.smart_config import Config
from icontroller import IController

class BaseApp:
    name = ""
    version = "0.0.1"
    module = "no_module"
    hidden = False
    
    def __init__(self, controller: IController):
        super().__init__()
        self.controller = controller
        self.config = Config(f"config/apps/{self.name}.json")
        self.controller.app_configs[self.name] = self.config
        print(f"BaseApp {self.name} {self.version}")

    async def setup(self):
        """
        Is called when the app is started.
        """
        
        return None

    async def teardown(self):
        """
        Is called when the app is stopped.
        """
        
        return None
    
    async def update(self):
        """
        Is called every 50 milliseconds.
        """
        
        return None
    
    def button_press(self, button):
        """
        Called when a button is pressed.
        """

        pass
    
    def button_click(self, button):
        """
        Called when a button is clicked (called on release, but is not called with a long press)
        """

        pass

    def button_release(self, button):
        """
        Called when a button is released.
        """

        pass

    def button_long_press(self, button):
        """
        Called when a button is long pressed.
        """

        pass
