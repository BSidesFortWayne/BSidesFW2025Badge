# Credit for most of this code: https://github.com/FreakiNiki/Imperial-March/blob/master/imperial_march.py
from apps.app import BaseApp
import gc9a01 
from machine import Pin, PWM
from time import sleep

tone_values = {'LA3': 220, 'F3': 174, 'C4': 261, 'E4': 329, 'F4': 349, 'Ab3': 207, 'LA4': 440, 'Ab4': 415, 'G4': 392, 'Gb4': 370, 'Bb3': 233, 'Eb4': 311, 'D4': 293, 'Db4': 277, 'B3': 247}
pin_piezo = Pin(15, Pin.OUT)

class ImperialMarch(BaseApp):
    name = "Imperial March"
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.display1 = self.controller.bsp.displays.display1
        print("Playing Imperial March")
        
        self.playsong()

    def beep(self, tone, time):
        for key in tone_values:
            if key == tone:
                value = tone_values[key]
        pwm = PWM(pin_piezo, freq=value, duty = 512)
        sleep(time)
        pwm.deinit()
        sleep(1/20)

    def playsong(self):
        sleep(1/2)
        self.beep('LA3', 1/2)
        self.beep('LA3', 1/2)
        self.beep('LA3', 1/2)
        self.beep('LA3', 1/2)
        self.beep('F3', 1/3)
        self.beep('C4', 1/6)
        self.beep('LA3', 1/2)
        self.beep('F3', 1/3)
        self.beep('C4', 1/6)
        self.beep('LA3', 1/2)
        sleep(1/2)
        self.beep('E4', 1/2)
        self.beep('E4', 1/2)
        self.beep('E4', 1/2)
        self.beep('F4', 1/3)
        self.beep('C4', 1/6)
        self.beep('Ab3', 1/2)
        self.beep('F3', 1/3)
        self.beep('C4', 1/6)
        self.beep('LA3', 1/2)
        sleep(1/2)
        self.beep('LA4', 1/2)
        self.beep('LA3', 1/3)
        self.beep('LA3', 1/6)
        self.beep('LA4', 1/2)
        self.beep('Ab4', 1/3)
        self.beep('G4', 1/6)
        self.beep('Gb4', 1/10)
        self.beep('E4', 1/10)
        self.beep('F4', 1/10)
        sleep(1/2)
        self.beep('Bb3', 1/6)
        self.beep('Eb4', 1/2)
        self.beep('D4', 1/3)
        self.beep('Db4', 1/6)
        self.beep('C4', 1/10)
        self.beep('B3', 1/10)
        self.beep('C4', 1/10)