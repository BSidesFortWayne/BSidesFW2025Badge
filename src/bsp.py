from drivers.leds import LEDs
from drivers.lis3dh import LIS3DH_I2C
from machine import Pin, I2C
from drivers.pca9535 import PCA9535
from drivers.buttons import Buttons
from drivers.audio import Speaker
from drivers.displays import Displays

class BSP:
    def __init__(self, hardware_version: str):
        print("Initializing BSP")
        print("I2C")
        # Initialize I2C on an ESP32 

        self.i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=400_000)
        self.leds = LEDs()
        self.iox = PCA9535(self.i2c)
        self.buttons = Buttons(hardware_version, self.iox)
        self.displays = Displays()
        self.imu = LIS3DH_I2C(self.i2c)
        self.speaker = Speaker()
        self.hardware_version = hardware_version
        print("BSP initialized")

class BSPHolder:
    def __init__(self, hardware_version: str):
        self._bsp = BSP(hardware_version)

    @property
    def bsp(self):
        return self._bsp