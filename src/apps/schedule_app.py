import framebuf
import asyncio
from apps.app import BaseApp
from ui.widget_app import WidgetApp
from ui.list_item import ListItem
from ui.stack_layout import StackLayout
from ui.common import Direction
from lib.microfont import MicroFont
from drivers.displays import rgb

class ScheduleApp(BaseApp, WidgetApp):
    name = "ScheduleApp"
    version = "0.1.0"

    def __init__(self, controller):
        BaseApp.__init__(self, controller)
        WidgetApp.__init__(self, controller)
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
        self.selected_category = "By Time"
        self.selected_item = "10:00 AM"
        self.layout = self.create_layout()
        self.display = self.controller.bsp.displays[0]

    def create_layout(self):
        layout = StackLayout(name="ScheduleLayout", direction=Direction.VERTICAL, spacing=5, padding=10)

        # Add category buttons
        for category in self.schedule.keys():
            layout.add_widget(
                ListItem(
                    title=category,
                    subtitle="",
                    selected=(category == self.selected_category),
                    name=f"Category_{category}",
                    title_font=MicroFont("fonts/victor_R_24.mfnt", cache_index=True, cache_chars=True),
                    subtitle_font=MicroFont("fonts/victor_R_18.mfnt", cache_index=True, cache_chars=True)
                )
            )

        # Add selected items
        items = self.schedule[self.selected_category]
        for item in items.keys():
            layout.add_widget(
                ListItem(
                    title=item,
                    subtitle=items[item],
                    selected=(item == self.selected_item),
                    name=f"Item_{item}",
                    title_font=MicroFont("fonts/victor_R_24.mfnt", cache_index=True, cache_chars=True),
                    subtitle_font=MicroFont("fonts/victor_R_18.mfnt", cache_index=True, cache_chars=True)
                )
            )

        return layout

    async def update(self):
        # Render the schedule app's UI
        self.layout.render(40, 0, self.fbuf, self.fbuf_width, self.fbuf_height)
        # Display the rendered buffer
        self.display.blit_buffer(
            self.fbuf_mem,
            0,
            0,
            self.fbuf_width,
            self.fbuf_height
        )

    def button_press(self, button):
        # Handle button presses to navigate the schedule
        print(f'X Button pressed: {button}')
        if button == 4:  # Up button
            self.select_previous_item()
        elif button == 5:  # Down button
            self.select_next_item()
        elif button == 6:  # Select button
            self.select_item()

    def select_previous_item(self):
        # Select the previous item in the current category
        items = list(self.schedule[self.selected_category].keys())
        current_index = items.index(self.selected_item)
        new_index = (current_index - 1) % len(items)
        self.selected_item = items[new_index]
        self.update_layout()

    def select_next_item(self):
        # Select the next item in the current category
        items = list(self.schedule[self.selected_category].keys())
        current_index = items.index(self.selected_item)
        new_index = (current_index + 1) % len(items)
        self.selected_item = items[new_index]
        self.update_layout()

    def select_item(self):
        # Handle item selection (e.g., show details)
        pass

    def update_layout(self):
        # Update the layout without recreating all widgets
        items = self.schedule[self.selected_category]
        for widget in self.layout.children:
            if isinstance(widget, ListItem) and widget.name.startswith("Item_"):
                item_name = widget.name.split("_")[1]
                widget.set_selected(item_name == self.selected_item)

# Example usage
if __name__ == "__main__":
    from single_app_runner import run_app
    run_app(ScheduleApp)  # type: ignore
