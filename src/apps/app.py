class BaseApp:
    name = "(No Name)"
    version = "0.0.1"
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
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
