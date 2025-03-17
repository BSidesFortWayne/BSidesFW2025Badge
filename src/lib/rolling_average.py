class RollingAverage:
    def __init__(self, window_size):
        self.window_size = window_size
        self.data = []
        self.total = 0

    def add(self, value):
        self.data.append(value)
        self.total += value

        if len(self.data) > self.window_size:
            self.total -= self.data.pop(0)