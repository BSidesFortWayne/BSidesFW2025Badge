from apps.app import BaseApp
import gc9a01 

class Menu(BaseApp):
    def __init__(self, controller):
        super().__init__(controller, "Main Menu")
        
        self.title_display = self.controller.bsp.displays.display1
        self.app_selection = self.controller.bsp.displays.display2
        self.display_center_text = self.controller.bsp.displays.display_center_text
        self.display_text = self.controller.bsp.displays.display_text

        self.menu_items = [
            "Badge",
            "Analog Clock",
            "Tetris"
        ]

        self.title_display.fill(gc9a01.BLACK)
        self.app_selection.fill(gc9a01.BLACK)

        self.display_center_text("Main Menu")
        for i, item in enumerate(self.menu_items):
            self.display_text(
                item,
                40,
                40 + (i * 40),
                display_index=2
            )

    
    def button_press(self, button: int):
        pass


    def update(self):
        pass


print("Menu loaded")