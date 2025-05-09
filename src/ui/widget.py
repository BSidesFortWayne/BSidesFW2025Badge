import framebuf
class Widget:
    def __init__(self, name: str):
        self.name = f"{name}{id(self)}"

    def __str__(self):
        return f"Widget: {self.name}"
    
    def __repr__(self):
        return f"<Widget {self.name}>"
    
    def render(self, x: int, y: int, fbuf: framebuf.FrameBuffer, fbuf_width: int = 240, fbuf_height: int = 240) -> tuple[int, int]:
        """
        Update the widget. This method should be implemented in the derived class.
        """
        raise NotImplementedError("Subclasses should implement this method.")
    