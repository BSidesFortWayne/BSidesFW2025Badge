from ui.widget import Widget
from ui.common import Direction
import framebuf


class StackLayout(Widget):
    def __init__(
            self, 
            *args,
            name: str = "",
            spacing: int = 0,
            padding: int = 0,
            direction: int = Direction.VERTICAL
        ):
        super().__init__(name)
        self.children: list[Widget] = []
        for child in args:
            if not isinstance(child, Widget):
                raise ValueError(f"Argument {child} is not a Widget")
            self.children.append(child)
            
        self.spacing = spacing
        self.padding = padding
        self.direction = direction

    def add_widget(self, widget: Widget, x: int, y: int):
        self.children.append(widget)

    def render(
            self, 
            x: int,
            y: int, 
            fbuf: framebuf.FrameBuffer, 
            fbuf_width: int = 240, 
            fbuf_height: int = 240
        ):
        start_x = x
        start_y = y
        spacing = self.spacing
        padding = self.padding
        for widget in self.children:
            width, height = widget.render(x + padding, y + padding, fbuf, fbuf_width, fbuf_height)
            if self.direction == Direction.VERTICAL:
                y += (height + spacing + padding)
            else:
                x += (width + spacing + padding)
        
        return x - start_x, y - start_y
