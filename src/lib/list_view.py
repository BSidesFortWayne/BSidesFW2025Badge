class ListView:
    def __init__(
            self, 
            items: list, 
            window_size: int, 
            peek_behind: int = 0, 
            peek_ahead: int = 0,
            selected_index: int = 0,
            wrap: bool = False):
        self.items = items
        self.window_size = window_size
        self.peek_behind = peek_behind
        self.peek_ahead = peek_ahead
        self.selected_index = selected_index
        self.wrap = wrap
    
    def get_visible_items(self):
        start_index = max(0, self.selected_index - self.peek_behind)
        end_index = min(len(self.items), self.selected_index + self.peek_ahead + 1)
        
        if self.wrap:
            if start_index < 0:
                start_index += len(self.items)
            if end_index > len(self.items):
                end_index -= len(self.items)
        
        return self.items[start_index:end_index]

    def move_selection(self, direction: int):
        if not self.wrap:
            new_index = self.selected_index + direction
            if new_index < 0 or new_index >= len(self.items):
                return
        else:
            new_index = (self.selected_index + direction) % len(self.items)
        self.selected_index = new_index

    def get_selected_item(self):
        if self.items:
            return self.items[self.selected_index]
        return None
    
    def set_selected_index(self, index: int):
        if 0 <= index < len(self.items):
            self.selected_index = index
        elif self.wrap:
            self.selected_index = index % len(self.items)
        else:
            raise IndexError("Index out of range")
        
    def get_selected_index(self):
        return self.selected_index
    
    def __len__(self):
        return len(self.items)
    
    def scroll_up(self):
        self.move_selection(-1)

    def scroll_down(self):
        self.move_selection(1)

