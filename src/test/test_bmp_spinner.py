from controller import Controller
import framebuf
import time

from img import bsides_logo


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

time_start = time.ticks_ms()
while True:
    # fbuf.fill(gc9a01.BLACK)

    c.bsp.displays.display1.bitmap(bsides_logo, x, y)
    
    frame_count += 1
    if frame_count % 100 == 0:
        time_end = time.ticks_ms()
        diff_s = (time_end - time_start) / 1000
        total_frames = frame_count - last_frame_count
        print(f'{total_frames / diff_s} FPS')
        time_start = time.ticks_ms()
        last_frame_count = frame_count
