from drivers.leds import LEDs
from drivers.lis3dh import LIS3DH_I2C
from machine import Pin, I2C, RTC
from drivers.pca9535 import PCA9535
from drivers.buttons import Buttons
from drivers.audio import Speaker
from drivers.bluetooth import Bluetooth

class BSP:
    def __init__(self, hardware_version: str, displays: Displays, debug: bool = False):
        def print_debug(message: str):
            if debug:
                print(message)
        print_debug("Initializing BSP")
        self.displays = displays
        self.i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=400_000)
        print_debug("I2C initialized")
        self.bluetooth = Bluetooth()
        print_debug("Bluetooth initialized")
        self.leds = LEDs()
        print_debug("LEDs initialized")
        self.iox = PCA9535(self.i2c)
        print_debug("PCA9535 initialized")
        self.buttons = Buttons(hardware_version, self.iox)
        print_debug("Buttons initialized")
        self.imu = LIS3DH_I2C(self.i2c)
        print_debug("IMU initialized")
        self.speaker = Speaker()
        print_debug("Speaker initialized")
        self.hardware_version = hardware_version
        print_debug(f"Hardware version: {self.hardware_version}")
        self.rtc = RTC()
        print_debug("RTC initialized")
        print_debug("BSP initialized")
