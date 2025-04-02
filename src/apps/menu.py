import asyncio
from apps.app import BaseApp
import gc9a01 
import framebuf

from hardware_rev import HardwareRev
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

        self.menu_items = sorted([str(app) for app in self.controller.app_directory])

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
    
    def menu_move_down(self):
        first = self.menu_items.pop(0)
        self.menu_items.append(first)
        
    def menu_move_up(self):
        last = self.menu_items.pop(-1)
        self.menu_items.insert(0, last)
    
    def button_press(self, button: int):
        if self.controller.bsp.hardware_version == HardwareRev.V3:
            if button == 4:
                self.menu_move_down()
            elif button == 5:
                self.menu_move_up()
            elif button == 6:
                self.controller.switch_app(self.menu_items[0])
        else:
            if button == 5:
                self.menu_move_down()
            elif button == 4:
                self.controller.switch_app(self.menu_items[0])

    async def update(self):
        # self.title_display.fill(gc9a01.BLACK)
        # self.app_selection.fill(gc9a01.BLACK)
        debug_mode = self.config['debug'].value()

        self.fbuf.fill(gc9a01.BLACK)
        for i, item in enumerate(self.menu_items[:5]):
            off_x, off_y = self.font.write(
                item, 
                self.fbuf_mv, 
                framebuf.RGB565, 
                self.fbuf_width, 
                self.fbuf_height, 
                0,
                i * 40,
                gc9a01.RED if i == 0 else gc9a01.WHITE
            )

            if debug_mode:
                self.fbuf.text(
                    f"{off_x}, {off_y}",
                    0,
                    i * 40,
                    gc9a01.WHITE
                )
            # generate rectangle around first item
            self.fbuf.rect(
                0,
                i * 40,
                off_x,
                off_y,
                gc9a01.RED if i == 0 else gc9a01.WHITE
            )


        self.controller.bsp.displays.display2.blit_buffer(
            self.fbuf_mv,
            40,
            40,
            self.fbuf_width,
            self.fbuf_height
        )
