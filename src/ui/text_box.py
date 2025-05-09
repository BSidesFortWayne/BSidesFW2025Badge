import framebuf

from lib.microfont import MicroFont
from ui.widget import Widget


class TextBox(Widget):
    def __init__(self, text: str = "", width: int = 20, height: int = 1, color='white', name: str = ''):
        super().__init__(name)
        self.text = text
        self.width = width
        self.height = height
        # TODO make this normalized 
        self.font = MicroFont("fonts/victor_R_24.mfnt", cache_index=True, cache_chars=True)

    def render(
            self, 
            x: int,
            y: int, 
            fbuf: framebuf.FrameBuffer, 
            fbuf_width: int = 240, 
            fbuf_height: int = 240
        ):
        # Render the text box with the specified dimensions
        return self.font.write(
            self.text,
            fbuf,
            framebuf.RGB565, 
            fbuf_width, 
            fbuf_height,
            x,
            y,
            0xFFFF,
        )

    def set_text(self, text: str):
        self.text = text

    def get_text(self) -> str:
        return self.text
    
