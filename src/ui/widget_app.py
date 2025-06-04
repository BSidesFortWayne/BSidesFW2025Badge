import framebuf
from lib.microfont import MicroFont

class WidgetApp:
    def __init__(self, controller):
        self.controller = controller
        self.fbuf_width = 240
        self.fbuf_height = 240
        self.fbuf_mem = bytearray(self.fbuf_width * self.fbuf_height * 2)
        self.fbuf = framebuf.FrameBuffer(
            self.fbuf_mem,
            self.fbuf_width,
            self.fbuf_height,
            framebuf.RGB565
        )
        self.font = MicroFont("fonts/victor_R_24.mfnt", cache_index=True, cache_chars=True)
    