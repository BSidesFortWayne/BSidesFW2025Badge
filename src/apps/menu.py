import asyncio
from apps.app import BaseApp
import gc9a01 
import framebuf

from lib.microfont import MicroFont

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

        # self.icons = [app.icon for app in self.controller.app_directory]


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

        self.fbuf_width = 200
        self.fbuf_height = 200

        self.fbuf_mem = bytearray(self.fbuf_width*self.fbuf_height*2)
        self.fbuf = framebuf.FrameBuffer(
            self.fbuf_mem, 
            self.fbuf_width, 
            self.fbuf_height, 
            framebuf.RGB565
        )
        self.fbuf_mv = memoryview(self.fbuf_mem)
        self.font = MicroFont("fonts/victor_R_24.mfnt", cache_index=True)

        self.render_lock = asyncio.Lock()


    def __del__(self):
        self.controller.bsp.buttons.button_pressed_callbacks.remove(self.button_press)
    
    def button_press(self, button: int):
        if button == 5:
            first = self.menu_items.pop(0)
            self.menu_items.append(first)
        elif button == 4:
            self.controller.switch_app(self.menu_items[0])

    async def update(self):
        # self.title_display.fill(gc9a01.BLACK)
        # self.app_selection.fill(gc9a01.BLACK)
        self.fbuf.fill(gc9a01.BLACK)
        for i, item in enumerate(self.menu_items[:5]):
            self.font.write(
                item, 
                self.fbuf_mv, 
                framebuf.RGB565, 
                self.fbuf_width, 
                self.fbuf_height, 
                0,
                i * 40,
                gc9a01.RED if i == 0 else gc9a01.WHITE
            )


        self.controller.bsp.displays.display2.blit_buffer(
            self.fbuf_mv,
            40,
            40,
            self.fbuf_width,
            self.fbuf_height
        )
