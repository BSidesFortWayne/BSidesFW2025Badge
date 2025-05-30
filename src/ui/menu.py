from ui.text_box import TextBox
from ui.common import Direction
from ui.stack_layout import StackLayout

import framebuf

class TextMenuWidget:
    def __init__(self, args, title: str):
        self.title = title

        # Validate that args is a dict of string/string or string/callable pairs?
        if not isinstance(args, dict):
            raise ValueError("MenuWidget requires a dictionary of items")
        
        self._items = list(args.keys())

        self.layout = StackLayout(name="MenuLayout", direction=Direction.VERTICAL, spacing=5, padding=10)
        for item in self._items:
            self.layout.add_widget(
                TextBox(text=item, height=20, width=100)
            )

        self.selected_box = self.layout.children[0]
        self.path = []
        self.highlight_color = (255, 255, 0)
        self.default_color = (255, 255, 255)

    def render(
        self, 
        x: int,
        y: int, 
        fbuf: framebuf.FrameBuffer, 
        fbuf_width: int = 240, 
        fbuf_height: int = 240
    ):
        self.layout.render(
            x=x, 
            y=y, 
            fbuf=fbuf, 
            fbuf_width=fbuf_width, 
            fbuf_height=fbuf_height
        )
