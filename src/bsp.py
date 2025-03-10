from hardware_rev import HardwareRev
from leds import LEDs
from lis3dh import LIS3DH_I2C
from machine import Pin, I2C
from pca9535 import PCA9535
from buttons import Buttons
import displays
from audio import Speaker


class BSP:
    def __init__(self, hardware_version: str):
        print("Initializing BSP")
        print("I2C")
        self.i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=400_000)
        print("LEDs")
        self.leds = LEDs()
        print("PCA9535")
        self.iox = PCA9535(self.i2c)
        print("Buttons")
        self.buttons = Buttons(hardware_version, self.iox)
        print("Displays")
        self.displays = displays
        print("IMU")
        self.imu = LIS3DH_I2C(self.i2c)
        print("Speaker")
        self.speaker = Speaker()
        print("Hardware version")
        self.hardware_version = hardware_version
        print("BSP initialized")
