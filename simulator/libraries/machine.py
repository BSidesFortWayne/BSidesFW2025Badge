import _thread
import time
import emulator

class Pin:
    IRQ_FALLING = 0
    IRQ_RISING = 1
    IN = 0
    OUT = 1

    def __init__(self, pin, mode=None):
        self.interrupts = []
        self._value = 0
        self.pin = pin
        self.mode = mode
    
    def init(self, *args, **kwargs):
        pass

    def value(self, state=None):
        emulator.send_command('pin', 'value', pin=self.pin, value=self._value)
        if state == None:
            return self._value
        else:
            self._value = state
    
    def on(self):
        self._value = 1
        emulator.send_command('pin', 'value', pin=self.pin, value=self._value)
    
    def off(self):
        self._value = 0
        emulator.send_command('pin', 'value', pin=self.pin, value=self._value)

    def irq(self, handler, trigger):
        self.interrupts.append({
            'handler': handler,
            'trigger': trigger
        })

class PWM:
    def __init__(self, pin):
        self.pin = pin
    
    def duty(self, value):
        emulator.send_command('pwm', 'duty', value=value)
    
    def freq(self, value):
        emulator.send_command('pwm', 'freq', value=value)

class I2C:
    def __init__(self, *args, **kwargs):
        pass

    def scan(self):
        return [0x18, 0x20]
    
    def start(self):
        pass

    def stop(self):
        pass

    def init(self):
        pass

    def readfrom(self, buffer, nack=True):
        return [0 for x in range(len(buffer))]
    
    def readinto(self, address, byte_amount, stop=True):
        return [0 for x in range(byte_amount)]

    def readfrom_mem(self, address, port, byte_amount, stop=True):
        return [0 for x in range(byte_amount)]
    
    def readfrom_mem_into(self, address, byte_amount, stop=True, addrsize=8):
        return [0 for x in range(byte_amount)]

    def writeto(self, address, buffer, stop=True):
        return len(buffer)
    
    def writeto_mem(self, address, memory_address, buffer, addrsize=8):
        return len(buffer)

    def writevto(self, address, vector, stop=True):
        return len(buffer)
    
    def write(self, buffer):
        return len(buffer)

class SPI:
    def __init__(self, *args, **kwargs):
        pass

class Timer:
    PERIODIC = 0

    def __init__(self, id):
        self.id = id
    
    def init(self, mode, period, callback):
        _thread.start_new_thread(self.timer_thread, (period, callback))
    
    def timer_thread(self, delay, function):
        while True:
            function(self)
            time.sleep_ms(delay)

class ADC:
    def __init__(self, *args, **kwargs):
        pass