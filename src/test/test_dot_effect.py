import framebuf
import time
import random

from bsp import BSP
from hardware_rev import HardwareRev

bsp = BSP(hardware_version=HardwareRev.V2)

fbuf_width = 240
fbuf_height = 240
x = 0
y = 0

mem_buf = bytearray(fbuf_width * fbuf_height * 2)

fbuf = framebuf.FrameBuffer(
    mem_buf, 
    fbuf_width,
    fbuf_height,
    framebuf.RGB565
)

color = 0xFFFF # Color must be in the framebuffer color mode format.

red_low = 120
red_high = 180

def rgb_to_565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | ((b & 0xF8) >> 3)


def _565_to_rgb(color):
    r = (color & 0xF800) >> 8
    g = (color & 0x07E0) >> 3
    b = (color & 0x001F) << 3

    return r, g, b


def interpolate_random_color(color1: int, color2: int):
    r1,g1,b1 = _565_to_rgb(color1)
    r2,g2,b2 = _565_to_rgb(color2)

    r = random.randint(r1, r2)
    g = random.randint(g1, g2)
    b = random.randint(b1, b2)

    return rgb_to_565(r, g, b)


# 1101 1110
# 0111 1011 = 0x7B

# blue green red?
# 0xFF 0xFF 0x00
MAGENTA = 0xF81F

color1 = rgb_to_565(0xff, 0xff, 0x10) # 0xd81f
# color2 = rgb_to_565(0x7b, 0x00, 0x94) # 0x7812
# color2 = rgb_to_565(180, 40, 180)

# colors = [color1, color2]

def get_random_purple():
    return color1
    # return random.choice(colors)
    # return interpolate_random_color(color1, color2)


frame_count = 0
time_start = time.ticks_ms()
last_frame_count = 0

while True:

    # 0xd81f = 0b 1101 1000 0001 1111
    #          0b 1111 1000 0001 1011 reversed bits
    #          0b 1111 0001 1000 1101

    fbuf.fill(color1)

    # Draw 100 random pixels
    # for i in range(300):
    #     x = random.randint(0, fbuf_width)
    #     y = random.randint(0, fbuf_height)
    #     fbuf.pixel(x, y, get_random_purple())
        # fbuf.pixel(x, y, random.randint(0, 0xFFFF))
    
    bsp.displays.display1.blit_buffer(
        mem_buf,
        x,
        y,
        fbuf_width,
        fbuf_height,
    )

    frame_count += 1
    if frame_count % 100 == 0:
        time_end = time.ticks_ms()
        diff_s = (time_end - time_start) / 1000
        total_frames = frame_count - last_frame_count
        print(f'{total_frames / diff_s} FPS')
        time_start = time.ticks_ms()
        last_frame_count = frame_count


