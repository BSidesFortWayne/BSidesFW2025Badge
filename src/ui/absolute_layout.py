from ui.widget import Widget
import framebuf


class AbsoluteLayoutItem:
    def __init__(self, widget: Widget, x: int, y: int):
        self.widget = widget
        self.x = x
        self.y = y

    def __repr__(self):
        return f"AbsoluteLayoutItem(widget={self.widget}, x={self.x}, y={self.y})"
    

class AbsoluteLayout(Widget):
    def __init__(
            self, 
            *args,
            name: str = "",
        ):
        super().__init__(name)
        self.name = name
        self.children: list[AbsoluteLayoutItem] = []
        # Make sure we have length // 3 args
        if len(args) % 3 != 0:
            raise ValueError("AbsoluteLayout requires a multiple of 3 arguments (widget, x, y)")

        for i in range(0, len(args), 3):
            widget = args[i]
            x = args[i + 1]
            y = args[i + 2]
            if not isinstance(widget, Widget):
                raise ValueError(f"Argument {i} is not a Widget")
            if not isinstance(x, int):
                raise ValueError(f"Argument {i + 1} is not an int")
            if not isinstance(y, int):
                raise ValueError(f"Argument {i + 2} is not an int")
            self.children.append(AbsoluteLayoutItem(widget, x, y))

    def add_widget(self, widget: Widget, x: int, y: int):
        self.children.append(AbsoluteLayoutItem(widget, x, y))

    def render(
            self, 
            x: int,
            y: int, 
            fbuf: framebuf.FrameBuffer, 
            fbuf_width: int = 240, 
            fbuf_height: int = 240
        ):
        for child in self.children:
            child.widget.render(x + child.x, y + child.y, fbuf, fbuf_width, fbuf_height)
