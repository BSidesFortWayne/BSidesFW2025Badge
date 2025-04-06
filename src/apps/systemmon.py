import gc9a01
from apps.app import BaseApp
import esp
import esp32
import framebuf

from fonts import arial32px
from single_app_runner import run_app

class SysMon(BaseApp):
    # This will be the name of the app that is displayed in the app menu
    name = "System Monitor"

    # This will be the version of the app that is displayed in the app menu
    version = "0.0.1"
    
    def __init__(self, controller):
        super().__init__(controller)
        self.font = arial32px

        self.fbuf_width = 240
        self.fbuf_height = 240
        self.fbuf_mem = bytearray(self.fbuf_width * self.fbuf_height * 2)
        self.fbuf_mv = memoryview(self.fbuf_mem)
        self.fbuf = framebuf.FrameBuffer(
            self.fbuf_mem, 
            self.fbuf_width, 
            self.fbuf_height, 
            framebuf.RGB565
        )

        self.config.add("x_offset", 0)
        self.config.add("y_offset", 0)

        
    async def update(self):
        raw_temp = esp32.raw_temperature()
        flash_size = esp.flash_size()
        partition = esp32.Partition.find()[0]
        part_info = partition.info()
        heap_data = esp32.idf_heap_info(esp32.HEAP_DATA)
        heap_exec = esp32.idf_heap_info(esp32.HEAP_EXEC)

        type, subtype, addr, size, label, encrypted = part_info
        # print(raw_temp)
        # print(flash_size)
        # print(part_info)
        # print(heap_data)
        # print(heap_exec)
        self.fbuf.fill(0)

        x_start = self.config['x_offset']
        y_start = self.config['y_offset']

        self.fbuf.text(f"Raw Temp: {raw_temp}",         x_start + 0, y_start + 0, gc9a01.WHITE)
        self.fbuf.text(f"Flash Size: {flash_size}",     x_start + 0, y_start + 20, gc9a01.WHITE)
        self.fbuf.text(f"Heap Data: {heap_data[0][0]}", x_start + 0, y_start + 40, gc9a01.WHITE)
        self.fbuf.text(f"Heap Exec: {heap_exec[0][0]}", x_start + 0, y_start + 60, gc9a01.WHITE)
        self.fbuf.text(f"Part. Size: {size}",           x_start + 0, y_start + 80, gc9a01.WHITE)

        self.controller.displays.display1.blit_buffer(
            self.fbuf_mv,
            0,
            0,
            self.fbuf_width,
            self.fbuf_height
        )


if __name__ == "__main__":
    run_app(SysMon)
