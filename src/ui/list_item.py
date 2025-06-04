import framebuf
from lib.microfont import MicroFont
from ui.widget import Widget
from drivers.displays import rgb

class ListItem(Widget):
    """
    A list item with title and optional subtitle.
    """
    def __init__(
            self, 
            title: str, 
            subtitle: str="", 
            selected: bool=False, 
            name: str="", 
            title_font: MicroFont | None = None, 
            subtitle_font: MicroFont | None = None
            ):
        super().__init__(name)
        self.title = title
        self.subtitle = subtitle
        self.selected = selected
        
        # Default fonts if not provided
        self.title_font = title_font or MicroFont("fonts/victor_R_24.mfnt", cache_index=True, cache_chars=True)
        if subtitle:
            self.subtitle_font = subtitle_font or MicroFont("fonts/victor_R_18.mfnt", cache_index=True, cache_chars=True)
        else:
            self.subtitle_font = None
            
        # Colors
        self.title_color = rgb((255, 255, 255))  # White
        self.subtitle_color = rgb((200, 200, 200))  # Light gray
        self.selection_color = rgb((0, 100, 255))  # Blue
        
        # Spacing
        self.padding = 5
        
    def set_selected(self, selected):
        """Set the selection state of this item"""
        self.selected = selected
        
    def render(self, x, y, fbuf, fbuf_width=240, fbuf_height=240):
        start_x = x
        start_y = y
        
        # Calculate total height first
        total_height = 0
        
        # Measure title height
        _, title_height = self.title_font.measure(self.title)
        total_height += title_height
        
        # Measure subtitle height if it exists
        subtitle_height = 0
        if self.subtitle and self.subtitle_font:
            _, subtitle_height = self.subtitle_font.measure(self.subtitle)
            total_height += subtitle_height + self.padding  # Add padding between title and subtitle
        
        # Draw selection background if selected
        if self.selected:
            # Draw a rectangle around the entire item
            fbuf.rect(
                x - self.padding, 
                y - self.padding,
                fbuf_width - 2 * x,  # Use available width
                total_height + 2 * self.padding,
                self.selection_color,
                True  # Fill the rectangle
            )
                
        # Draw title
        title_width, title_height = self.title_font.write(
            self.title,
            fbuf,
            framebuf.RGB565,
            fbuf_width,
            fbuf_height,
            x,
            y,
            self.title_color
        )
        
        y += title_height + self.padding
        
        # Draw subtitle if it exists
        if self.subtitle and self.subtitle_font:
            subtitle_width, subtitle_height = self.subtitle_font.write(
                self.subtitle,
                fbuf,
                framebuf.RGB565,
                fbuf_width,
                fbuf_height,
                x,
                y,
                self.subtitle_color
            )
            y += subtitle_height
        
        # Return the dimensions of the rendered item
        return fbuf_width - 2 * start_x, y - start_y
