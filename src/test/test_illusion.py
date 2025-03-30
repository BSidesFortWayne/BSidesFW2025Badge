import array
import gc9a01
from controller import Controller
import framebuf
import time


c = Controller()

c.bsp.displays.display1.fill(0x000000)

frame_count = 0
last_frame_count = 0

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

def rgb_to_565(r: int, g: int, b: int):
    return (r & 0xF8) | ((g & 0xE0) >> 5) | ((g & 0x1C) << 11) | ((b & 0xF8) << 5)

center_x = fbuf_width // 2
center_y = fbuf_height // 2

triangle_base = 80
triangle_half_base = triangle_base // 2
triangle_height = 69
triangle_half_height = triangle_height // 2

time_start = time.ticks_ms()
while True:
    fbuf.fill(gc9a01.BLACK)

    # fill half of the screen with black
    fbuf.fill_rect(
        0,
        0,
        fbuf_width // 2,
        fbuf_height,
        gc9a01.BLACK
    )

    # fill the other half with white
    fbuf.fill_rect(
        center_x,
        0,
        fbuf_width // 2,
        fbuf_height,
        gc9a01.WHITE
    )

    fbuf.poly(
        center_x,
        center_y,
        array.array('h', [
                              0, - triangle_half_height,
            -triangle_half_base, + triangle_half_height,
             triangle_half_base, + triangle_half_height,
                              0, - triangle_half_height,
        ]),
        rgb_to_565(128, 128, 128),
        True,
    )

    c.bsp.displays.display1.blit_buffer(
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
