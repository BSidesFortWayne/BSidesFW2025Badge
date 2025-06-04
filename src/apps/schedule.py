import asyncio
from apps.app import BaseApp
import gc9a01 
import framebuf

from hardware_rev import HardwareRev
from lib import queue
from lib.microfont import MicroFont
from lib.smart_config import BoolDropdownConfig


SELECTED_INDEX = 2
MOVE_DOWN = 1
MOVE_UP = -1
MOVE_IN = 2
MOVE_OUT = -2

class Schedule(BaseApp):
    name = "Schedule"
    hidden = True
    
    def __init__(self, controller):
        super().__init__(controller)
        
        self.title_display = self.controller.bsp.displays.display1
        self.app_selection = self.controller.bsp.displays.display2
        self.display_center_text = self.controller.bsp.displays.display_center_text
        self.display_text = self.controller.bsp.displays.display_text

        self.schedule = {
            "By Speaker": {
                "Alice": "Alice's Talk",
                "Bob": "Bob's Talk",
                "Charlie": "Charlie's Talk",
            },
            "By Time": {
                "10:00 AM": "Opening Remarks",
                "11:00 AM": "Keynote Speech",
                "12:00 PM": "Lunch Break",
                "1:00 PM": "Panel Discussion",
                "2:00 PM": "Workshops",
                "3:00 PM": "Closing Ceremony",
            },
            "By Room": {
                "Room A": "Workshop A",
                "Room B": "Workshop B",
                "Room C": "Panel Discussion",
                "Room D": "Keynote Speech",
            },
            "By Track": {
                "Track 1": "Introduction to Python",
                "Track 2": "Advanced Python Techniques",
                "Track 3": "Python for Data Science",
                "Track 4": "Python for Web Development",
            },
        }
        self.selected_index = 2
        self.focus_index = 2
        self.path = []
        self.items = list(self.schedule.keys())
        self.display_items = [self.items[i % len(self.items)] for i in range(self.selected_index - 2, self.selected_index + 4)]

        self.config.add("x_offset", 40)
        self.config.add("y_offset", 0)
        self.config.add("animate", BoolDropdownConfig("Animate", default=False))

        self.title_display.fill(gc9a01.BLACK)
        self.app_selection.fill(gc9a01.BLACK)

        self.display_center_text("Main Menu")

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

    def put_queue_action(self, action):
        try:
            self.queue.put_nowait(action)
        except queue.QueueFull:
            self.queue.get_nowait()
            self.queue.put_nowait(action)

    async def teardown(self):
        self.title_display.fill(gc9a01.BLACK)
        self.app_selection.fill(gc9a01.BLACK)


    def menu_move_down(self):
        self.put_queue_action(MOVE_DOWN)
        
    def menu_move_up(self):
        # last = self.menu_items.pop(-1)
        # self.menu_items.insert(0, last)
        self.put_queue_action(MOVE_UP)
    
    def navigate_deeper(self):
        pass
    
    def button_press(self, button: int):
        print(f"Menu button press {button}")
        if self.controller.bsp.hardware_version == HardwareRev.V3:
            if button == 7:
                self.navigate_deeper()
            if button == 4:
                self.menu_move_down()
            elif button == 5:
                self.menu_move_up()
            elif button == 6:
                asyncio.create_task(self.controller.switch_app(self.items[SELECTED_INDEX]))
        else:
            if button == 5:
                self.menu_move_down()
            elif button == 4:
                asyncio.create_task(self.controller.switch_app(self.items[SELECTED_INDEX]))

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

        display_items = self.items

        if not self.queue.empty():
            direction = await self.queue.get()
            if animate:
                for i in range(0, menu_item_height, 5):
                    print(fbuf_width*i*2, fbuf_width*(fbuf_height - i)*2, y_offset + (i*direction), fbuf_width, fbuf_height - i)
                    self.controller.bsp.displays.display2.blit_buffer(
                        fbuf_mv[fbuf_width*i*2:] if direction == MOVE_UP else fbuf_mv[:fbuf_width*(fbuf_height - i)*2],
                        x_offset,
                        y_offset,
                        fbuf_width,
                        fbuf_height - i,
                    )
                    await asyncio.sleep(0.01)

            self.selected_index = (self.selected_index + direction) % len(self.items)
            item_count = len(self.items)
            display_items = [self.items[i % item_count] for i in range(self.selected_index - 2, self.selected_index + 4)] if (len(self.items) > 5) else self.items
            

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

        self.items = display_items


if __name__ == "__main__":
    from single_app_runner import run_app
    run_app(Schedule) # type: ignore)
    