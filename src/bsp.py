from hardware_rev import HardwareRev
from leds import LEDs
from lis3dh import LIS3DH_I2C
from machine import Pin, I2C # type: ignore
from pca9535 import PCA9535
from buttons import Buttons
import displays
from audio import Speaker


class BSP:
    def __init__(self, hardware_version: str):
        self.i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=400_000)
        self.leds = LEDs()
        self.iox = PCA9535(self.i2c)
        self.buttons = Buttons(HardwareRev.V2, self.iox)
        self.displays = displays
        self.imu = LIS3DH_I2C(self.i2c)
        self.speaker = Speaker()
        self.hardware_version = hardware_version
