# Credit for most of this code: https://github.com/FreakiNiki/Imperial-March/blob/master/imperial_march.py
from apps.app import BaseApp
import gc9a01 
from time import sleep

class ImperialMarch(BaseApp):
    name = "Imperial March"
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.display1 = self.controller.bsp.displays.display1
        print("Playing Imperial March")
        
        self.controller.bsp.speaker.start_song('imperialmarch', repeat=True)
