from drivers.displays import rgb
from ui.text_box import TextBox
from ui.widget import Widget
import framebuf
from ui.common import Direction

class TableLayout(Widget):
    def __init__(
            self, 
            *args,
            name: str = "",
            column_width: int | list = 1,
            row_height: int | list = 0,
            col_width: int = 0,
            spacing: int = 0,
            padding: int = 0,
            cell_highlight: tuple | None = None,
        ):
        super().__init__(name)
        self.rows: list[list[Widget]] = []
        self.cell_highlight = None
        
        self.row_height = row_height
        self.col_width = col_width
        self._column_count = None
        for row in args:
            if not isinstance(row, list):
                raise ValueError(f"Argument {row} is not a Widget")
            if not self._column_count:
                self._column_count = len(row)
            elif len(row) != self._column_count:
                raise ValueError(f"All rows must have the same number of columns, got {len(row)}")

            self.rows.append([])
            for widget in row:
                if isinstance(widget, str):
                    self.rows[-1].append(
                        TextBox(
                            widget
                        )
                    )
                elif isinstance(widget, Widget):
                    self.rows[-1].append(widget)
        
        self.row_highlight = None
        self.column_highlight = None
        self.cell_highlight = cell_highlight
        
        if isinstance(column_width, int):
            self._column_width = [column_width] * len(self.rows[0])
        elif isinstance(column_width, list):
            if len(column_width) != len(self.rows[0]):
                raise ValueError(f"Column width list must match number of columns, got {len(column_width)}")
            self._column_width = column_width
        else:
            raise ValueError("Column width must be an int or a list of ints")
        
        if isinstance(row_height, int):
            self.row_height = [row_height] * len(self.rows)
        elif isinstance(row_height, list):
            if len(row_height) != len(self.rows):
                raise ValueError(f"Row height list must match number of rows, got {len(row_height)}")
            self.row_height = row_height
        else:
            raise ValueError("Row height must be an int or a list of ints")
            
        self.spacing = spacing
        self.padding = padding

    def add_row(self, *args):
        if len(args) != self._column_width:
            raise ValueError(f"TableLayout requires {self._column_width} columns, got {len(args)}")
        for child in args:
            if not isinstance(child, Widget):
                raise ValueError(f"Argument {child} is not a Widget")

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
        width = 0
        height = 0
        for row_index,row in enumerate(self.rows):
            for column_index,widget in enumerate(row):
                if (row_index, column_index) == self.cell_highlight:
                    fbuf.rect(
                        x, 
                        y, 
                        width + padding * 2, 
                        height + padding * 2, 
                        rgb((0, 100, 0)),  # Highlight color
                        True  # Fill the rectangle
                    )
                width, height = widget.render(x + padding, y + padding, fbuf, fbuf_width, fbuf_height)
                fbuf.rect(
                    x, 
                    y, 
                    width + padding * 2, 
                    height + padding * 2, 
                    0xFFFF,  # Fill color
                    False  # Fill the rectangle
                )
                x += width + self.spacing + padding * 2
            # y += self.row_height[row_index] + self.spacing
            y += height + spacing + padding * 2
            x = start_x

        
        return x - start_x, y - start_y
