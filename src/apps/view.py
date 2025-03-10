class BaseApp:
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

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
