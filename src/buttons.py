from machine import Pin

class Buttons:
    def __init__(self):
        self.button_io = [0, 33, 35, 34]
        self.button_objects = []
        self.button_callback = lambda: None

        for index, pin in enumerate(self.button_io):
            self.button_objects.append(Pin(pin, Pin.IN))
            self.button_objects[index].irq(handler=self.button_handler, trigger=Pin.IRQ_FALLING)

    def button_handler(self, pin):
            # find standard button number
            button = self.button_objects.index(pin)+1

            print(f'Button {button}, pin {pin} was pressed.')
            self.button_callback(button)
