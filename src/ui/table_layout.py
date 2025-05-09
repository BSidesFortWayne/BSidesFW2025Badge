from ui.widget import Widget
import framebuf
from ui.common import Direction

class TableLayout(Widget):
    def __init__(
            self, 
            *args,
            name: str = "",
            columns: int = 1,
            row_height: int = 0,
            col_width: int = 0,
            spacing: int = 0,
            padding: int = 0,
            fill_direction: int = Direction.VERTICAL
        ):
        super().__init__(name)
        self.children: list[Widget] = []
        self.columns = columns
        self.row_height = row_height
        self.col_width = col_width
        for child in args:
            if not isinstance(child, Widget):
                raise ValueError(f"Argument {child} is not a Widget")
            self.children.append(child)
            
        self.spacing = spacing
        self.padding = padding
        self.direction = fill_direction

    def add_row(self, *args):
        if len(args) != self.columns:
            raise ValueError(f"TableLayout requires {self.columns} columns, got {len(args)}")
        for child in args:
            if not isinstance(child, Widget):
                raise ValueError(f"Argument {child} is not a Widget")
            self.children.append(child)

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
