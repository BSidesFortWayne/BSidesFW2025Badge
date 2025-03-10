# color_setup.py Customise for your hardware config

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2024 Peter Hinch

# As written, supports:
# gc9a01 240x240 circular display on Pi Pico
# Pin mapping is for Waveshare RP2040-Touch-LCD-1.28
# Edit the driver import for other displays.

# Demo of initialisation procedure designed to minimise risk of memory fail
# when instantiating the frame buffer. The aim is to do this as early as
# possible before importing other modules.

# WIRING
# Pico      Display
# GPIO Pin
# 3v3  36   Vin
# IO6   9   CLK  Hardware SPI0
# IO7  10   DATA (AKA SI MOSI)
# IO8  11   DC
# IO9  12   Rst
# Gnd  13   Gnd
# IO10 14   CS

from machine import Pin, SPI
import gc
from drivers.gc9a01.gc9a01 import GC9A01 as SSD

# from drivers.gc9a01.gc9a01_8_bit import GC9A01 as SSD

DC1 = 19
RST1 = 14
CS1 = 33

DC2 = 25
RST2 = 27
CS2 = 13

prst1 = Pin(RST1, Pin.OUT)
pcs1  = Pin(CS1, Pin.OUT)
pdc1  = Pin(DC1, Pin.OUT)

prst2 = Pin(RST2, Pin.OUT)
pcs2  = Pin(CS2, Pin.OUT)
pdc2  = Pin(DC2, Pin.OUT)

gc.collect()  # Precaution before instantiating framebuf
# See DRIVERS.md
spi = SPI(1, sck=Pin(10), mosi=Pin(11), miso=Pin(12), baudrate=60_000_000)
ssd1 = SSD(spi, dc=pdc1, cs=pcs1, rst=prst1, lscape=False, usd=False, mirror=False)
ssd2 = SSD(spi, dc=pdc2, cs=pcs2, rst=prst2, lscape=False, usd=False, mirror=False)

from gui.core.ugui import Display, quiet


nxt = Pin(0, Pin.IN, Pin.PULL_UP)  # Move to next control
# sel = Pin(16, Pin.IN, Pin.PULL_UP)  # Operate current control
# prev = Pin(18, Pin.IN, Pin.PULL_UP)  # Move to previous control
# increase = Pin(20, Pin.IN, Pin.PULL_UP)  # Increase control's value
# decrease = Pin(17, Pin.IN, Pin.PULL_UP)  # Decrease control's value


display1 = Display(ssd1, nxt, nxt)

