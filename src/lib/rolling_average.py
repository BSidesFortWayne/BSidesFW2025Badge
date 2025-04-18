import micropython

class RollingAverage:
    def __init__(self, window_size = 100):
        self.window_size = window_size
        self.data: list[float] = []
        self.count: int = 0

    @micropython.native
    def add(self, value: int | float):
        self.data.append(value)

        if len(self.data) > self.window_size:
            # TODO make this more efficient index based logic instead of doing pop(...)
            self.data.pop(0)
        else:
            self.count += 1
    
    @micropython.native
    def last(self) -> float:
        if len(self.data) == 0:
            return 0
        return self.data[-1]
    
    @micropython.native
    def average(self) -> float:
        if len(self.data) == 0:
            return 0.0
        return sum(self.data) / len(self.data)