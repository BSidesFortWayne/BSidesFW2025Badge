from lib.smart_config import Config, SmartConfig

class BaseApp:
    name = "no_name"
    version = "0.0.1"
    module = "no_module"
    def __init__(self, controller):
        super().__init__()
        print(self.name)
        self.controller = controller
        self.config = Config(f"config/apps/{self.name}.json")
        print(f"BaseApp {self.name} {self.version}")

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
