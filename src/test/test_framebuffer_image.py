import framebuf
import time

import machine
from machine import Pin, SPI

USE_PY_DRIVER = True
if USE_PY_DRIVER:
    from drivers.gc9a01 import GC9A01
else:
    from gc9a01 import GC9A01


SCK = 18
MOSI = 23

DC1 = 19
RST1 = 14
CS1 = 33
DISP_EN = 32

machine.freq(240_000_000)
spi = SPI(1, baudrate=80_000_000, sck=Pin(SCK), mosi=Pin(MOSI))

dc = Pin(DC1, Pin.OUT)
rst = Pin(RST1, Pin.OUT)
cs = Pin(CS1, Pin.OUT)

backlight = Pin(DISP_EN, Pin.OUT)

display = GC9A01(
    spi, 
    240, 
    240, 
    dc=dc, 
    cs=cs, 
    reset=rst, 
    backlight=backlight,
    buffer_size=8192,
    rotation=3
)
display.fill_rect(
    0, 
    0, 
    240, 
    240, 
    0xF800
)

mem_buf = bytearray(240*240*2)
fbuf_mem = memoryview(mem_buf)
fbuf = framebuf.FrameBuffer(
    fbuf_mem, 
    240, 
    240, 
    framebuf.RGB565
)


while True:
    t_start = time.time_ns()

    fbuf.fill(0x0000)
    t_end = time.time_ns()
    elapsed_time = (t_end - t_start) / 1_000_000
    time.sleep_ms(20)
    print(f"Elapsed time: {elapsed_time:.2f} ms")
