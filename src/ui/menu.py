from ui.widget import Widget
from ui.text_box import TextBox
from ui.common import Direction
from ui.stack_layout import StackLayout

import framebuf

class TextMenuWidget(Widget):
    def __init__(self, args, title: str, path: list = []):
        self.title = title

        # Validate that args is a dict of string/string or string/callable pairs?
        if not isinstance(args, dict):
            raise ValueError("MenuWidget requires a dictionary of items")

        # self._items = sorted(list(args.keys()))

        self.args = args
        self.path = path
        self.highlight_color = (255, 255, 0)
        self.default_color = (255, 255, 255)

        self.selection_to_layout(self.args)

    def on_button_press(self, button_index):
        """Handle button press events for navigation."""
        # Get the current items at the current path
        current_items = self.get_items_in_path(self.args)

        # If current items are a dictionary, navigate to the next level
        if isinstance(current_items, dict):
            # Get the list of keys at the current level
            keys = list(current_items.keys())

            # Calculate the new index based on the button press
            # For simplicity, we'll assume button 0 is "up" and button 1 is "down"
            if button_index == 0:  # Up button
                if self.current_index > 0:
                    self.current_index -= 1
            elif button_index == 1:  # Down button
                if self.current_index < len(keys) - 1:
                    self.current_index += 1

            # Update the path to the selected item
            selected_key = keys[self.current_index]
            self.path.append(selected_key)

            # Update the layout with the new path
            self.selection_to_layout(self.args)

    def selection_to_layout(self, items: dict):
        items = self.get_items_in_path(items)
        # if an int, show the int edit widget
        if isinstance(items, int):
            self.layout = StackLayout(name="IntEditLayout", direction=Direction.VERTICAL, spacing=5, padding=10)
            self.layout.add_widget(
                TextBox(text=str(items), height=20, width=100)
            )
        # if a string, show the string edit widget
        elif isinstance(items, str):
            self.layout = StackLayout(name="StringEditLayout", direction=Direction.VERTICAL, spacing=5, padding=10)
            self.layout.add_widget(
                TextBox(text=items, height=20, width=100)
            )
        # if a dict, show the sub-menu
        elif isinstance(items, dict):
            self.layout = self.make_list(sorted(list(items.keys())))
        # if a list, show the list
        elif isinstance(items, list):
            self.layout = self.make_list(sorted(items))
        else:
            raise ValueError(f"Unsupported item type: {type(items)}")

    def make_list(self, items: list):
        layout = StackLayout(name="ListLayout", direction=Direction.VERTICAL, spacing=5, padding=10)
        for item in items:
            layout.add_widget(
                TextBox(text=item, height=20, width=100)
            )

        return layout

    def get_items_in_path(self, items: dict):
        for key in self.path:
            if key not in items:
                raise ValueError(f"Key {key} not found in items")

            items = items[key]

        return items

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
