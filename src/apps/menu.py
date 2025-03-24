from apps.app import BaseApp
import gc9a01 


class IconMenu(BaseApp):
    name = "Icon Menu"
    version = "0.0.1"
    def __init__(self, controller):
        super().__init__(controller)
        self.display1 = self.controller.bsp.displays.display1
        self.display2 = self.controller.bsp.displays.display2

        self.display1.fill(gc9a01.WHITE)
        self.display2.fill(gc9a01.WHITE)

        self.icon_size = 40
        self.icon_spacing = 10
        self.icons_per_row = 5
        self.icon_rows = 3

        self.icons = [app.icon for app in self.controller.app_directory]


class Menu(BaseApp):
    name = "Menu"
    def __init__(self, controller):
        super().__init__(controller)
        
        self.title_display = self.controller.bsp.displays.display1
        self.app_selection = self.controller.bsp.displays.display2
        self.display_center_text = self.controller.bsp.displays.display_center_text
        self.display_text = self.controller.bsp.displays.display_text

        self.menu_items = [str(app) for app in self.controller.app_directory]

        self.title_display.fill(gc9a01.BLACK)
        self.app_selection.fill(gc9a01.BLACK)

        self.display_center_text("Main Menu")
        # for i, item in enumerate(self.menu_items):
        #     self.display_text(
        #         item,
        #         40,
        #         40 + (i * 40),
        #         display_index=2
        #     )
        self.controller.bsp.buttons.button_pressed_callbacks.append(self.button_press)

    def __del__(self):
        self.controller.bsp.buttons.button_pressed_callbacks.remove(self.button_press)
    
    def button_press(self, button: int):
        if button == 5:
            first = self.menu_items.pop(0)
            self.menu_items.append(first)
        elif button == 4:
            last = self.menu_items.pop()
            self.menu_items.insert(0, last)


    def update(self):
        for i, item in enumerate(self.menu_items):
            if i == 0:
                # Draw a red line below the first item
                self.display_text(
                    item,
                    40,
                    40 + (i * 40),
                    display_index=2,
                    fg=gc9a01.RED
                )
            else:
                self.display_text(
                    item,
                    40,
                    40 + (i * 40),
                    display_index=2
                )

