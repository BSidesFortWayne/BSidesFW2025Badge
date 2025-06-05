import asyncio
from apps.app import BaseApp
import gc9a01 
import framebuf

from hardware_rev import HardwareRev
from lib import queue
from lib.microfont import MicroFont
from lib.smart_config import BoolDropdownConfig

# class IconMenu(BaseApp):
#     name = "Icon Menu"
#     version = "0.0.1"
#     def __init__(self, controller):
#         super().__init__(controller)
#         self.display1 = self.controller.bsp.displays.display1
#         self.display2 = self.controller.bsp.displays.display2

#         self.display1.fill(gc9a01.WHITE)
#         self.display2.fill(gc9a01.WHITE)

#         self.icon_size = 40
#         self.icon_spacing = 10
#         self.icons_per_row = 5
#         self.icon_rows = 3

#         # self.icons = [app.icon for app in self.controller.app_directory]

SELECTED_INDEX = 2
DOWN = 1
UP = -1
class Menu(BaseApp):
    name = "Menu"
    hidden = True
    
    def __init__(self, controller):
        super().__init__(controller)
        
        self.title_display = self.controller.bsp.displays.display1
        self.app_selection = self.controller.bsp.displays.display2
        self.display_center_text = self.controller.bsp.displays.display_center_text
        self.display_text = self.controller.bsp.displays.display_text

        self.menu_items = sorted([str(app) for app in self.controller.app_directory if not app.hidden])
        self.selected_index = 0
        self.focus_index = 2
        item_count = len(self.menu_items)
        self.display_items = [self.menu_items[i % item_count] for i in range(self.selected_index - 2, self.selected_index + 4)]

        self.config.add("x_offset", 40)
        self.config.add("y_offset", 0)
        self.config.add("animate", BoolDropdownConfig("Animate", default=False))

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

        self.fbuf_width = 200
        self.fbuf_height = 240

        self.fbuf_mem = bytearray(self.fbuf_width*self.fbuf_height*2)
        self.fbuf = framebuf.FrameBuffer(
            self.fbuf_mem, 
            self.fbuf_width, 
            self.fbuf_height, 
            framebuf.RGB565
        )
        self.fbuf_mv = memoryview(self.fbuf_mem)
        self.font = MicroFont("fonts/victor_R_24.mfnt", cache_index=True, cache_chars=True)

        self.queue = queue.Queue(maxsize=10)
        self.index = 0

    def put_queue_action(self, direction):
        try:
            self.queue.put_nowait(direction)
        except queue.QueueFull:
            self.queue.get_nowait()
            self.queue.put_nowait(direction)

    async def teardown(self):
        self.title_display.fill(gc9a01.BLACK)
        self.app_selection.fill(gc9a01.BLACK)


    def menu_move_down(self):
        self.put_queue_action(DOWN)
        
    def menu_move_up(self):
        # last = self.menu_items.pop(-1)
        # self.menu_items.insert(0, last)
        self.put_queue_action(UP)
    
    def button_press(self, button: int):
        print(f"Menu button press {button}")
        if self.controller.bsp.hardware_version == HardwareRev.V3:
            if button == 4:
                self.menu_move_down()
            elif button == 5:
                self.menu_move_up()
            elif button == 6:
                asyncio.create_task(self.controller.switch_app(self.display_items[SELECTED_INDEX]))
        else:
            if button == 5:
                self.menu_move_down()
            elif button == 4:
                asyncio.create_task(self.controller.switch_app(self.display_items[SELECTED_INDEX]))

    async def update(self):
        debug_mode = False
        x_offset = self.config['x_offset']
        y_offset = self.config['y_offset']
        menu_item_height = 40
        fbuf_width = self.fbuf_width
        fbuf_height = self.fbuf_height
        fbuf_mv = self.fbuf_mv
        fbuf = self.fbuf
        display = self.controller.bsp.displays.display2
        animate = self.config['animate'].value()

        display_items = self.display_items

        if not self.queue.empty():
            direction = await self.queue.get()
            if animate:
                for i in range(0, menu_item_height, 5):
                    print(fbuf_width*i*2, fbuf_width*(fbuf_height - i)*2, y_offset + (i*direction), fbuf_width, fbuf_height - i)
                    self.controller.bsp.displays.display2.blit_buffer(
                        fbuf_mv[fbuf_width*i*2:] if direction == UP else fbuf_mv[:fbuf_width*(fbuf_height - i)*2],
                        x_offset,
                        y_offset,
                        fbuf_width,
                        fbuf_height - i,
                    )
                    await asyncio.sleep(0.01)

            self.selected_index = (self.selected_index + direction) % len(self.menu_items)
            item_count = len(self.menu_items)
            display_items = [self.menu_items[i % item_count] for i in range(self.selected_index - 2, self.selected_index + 4)]
            

        fbuf.fill(gc9a01.BLACK)
        for i, item in enumerate(display_items):
            off_x, off_y = self.font.write(
                item, 
                fbuf_mv, 
                framebuf.RGB565, 
                fbuf_width, 
                fbuf_height, 
                0,
                i * menu_item_height,
                gc9a01.WHITE
            )

            if debug_mode:
                fbuf.text(
                    f"{off_x}, {off_y}",
                    0,
                    i * menu_item_height,
                    gc9a01.WHITE
                )

            if i == SELECTED_INDEX:
                # generate rectangle around first item
                fbuf.rect(
                    0,
                    i * 40,
                    off_x,
                    off_y,
                    gc9a01.RED
                )

        display.blit_buffer(
            fbuf_mv,
            x_offset,
            y_offset,
            fbuf_width,
            fbuf_height
        )

        self.display_items = display_items

        self.controller.battery.draw_battery(self.controller.displays.display1, (120-15, 240-60))
