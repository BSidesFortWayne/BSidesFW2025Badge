class BaseApp:
    def __init__(self, controller, name: str = "", version="0.0.1"):
        super().__init__()
        self.controller = controller
        self.name = name if name else "Da App"
        self.version = version
        print(f"BaseApp {self.name} {self.version}")

    def update(self):
        """
        Is called every 50 milliseconds.
        """
        
        pass
    
    def button_press(self, button):
        """
        Called when a button is pressed.
        """

        pass
