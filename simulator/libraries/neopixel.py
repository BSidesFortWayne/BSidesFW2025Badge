import emulator

class NeoPixel:
    def __init__(self, pin, number_of_leds):
        self.number_of_leds = number_of_leds
        self.leds = [(0, 0, 0) for x in range(self.number_of_leds)]

    def __getitem__(self, index):
        return self.leds[index]

    def __setitem__(self, index, value):
        self.leds[index] = value
    
    def __len__(self):
        return self.number_of_leds
    
    def write(self):
        emulator.send_command('neopixel', 'write', leds=self.leds)

    def fill(self, color):
        self.leds = [color for x in range(self.number_of_leds)]
