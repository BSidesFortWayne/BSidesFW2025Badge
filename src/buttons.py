import time
from machine import Pin, Timer

class Buttons:
    def __init__(self, i2c):
        self.i2c = i2c
        self.button_io = [0]
        self.button_objects = []
        self.debounce_time = 20
        self.last_press = 0
        self.button_callback = lambda: None
        self.timer = Timer(0)
        self.i2c.writeto_mem(0x20, 0x06, b'\xFF')
        self.i2c.writeto_mem(0x20, 0x07, b'\xFF')

        for index, pin in enumerate(self.button_io):
            self.button_objects.append(Pin(pin, Pin.IN))
            self.button_objects[index].irq(handler=self.irq_button_handler, trigger=Pin.IRQ_FALLING)

        self.i2c_last_button_states = [False for x in range(5)]
        self.timer.init(period=10, callback=self.read_pca9535_inputs)

    def read_pca9535_inputs(self, x):
        port0 = self.i2c.readfrom_mem(0x20, 0x00, 1)[0]
    
        port1 = self.i2c.readfrom_mem(0x20, 0x01, 1)[0]
    
        button_inputs = [
            not (port0 & (1 << 1)),
            not (port0 & (1 << 2)),
            not (port1 & (1 << 0)),
            not (port1 & (1 << 1)),
            not (port1 & (1 << 2))
        ]

        for index, button in enumerate(button_inputs):
            if not self.i2c_last_button_states[index] == button and button == True: # button pressed
                self.button_handler(index+1+len(self.button_io))
        
        self.i2c_last_button_states = button_inputs

    def irq_button_handler(self, pin):
            # find standard button number
            button = self.button_objects.index(pin)+1
            self.button_handler(button)

    def button_handler(self, pin_number):
        if self.last_press+self.debounce_time >= time.ticks_ms(): # debounce
                return
        print(f'Button {pin_number} was pressed.')
        self.button_callback(pin_number)
        self.last_press = time.ticks_ms()
