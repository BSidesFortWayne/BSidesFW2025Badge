import framebuf
import time

from bsp import BSP
from hardware_rev import HardwareRev
from lib.microfont import MicroFont

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

font = MicroFont("fonts/victor_B_70.mfnt", cache_index=True)

color = 0xFFFF # Color must be in the framebuffer color mode format.
angle = 0

frame_count = 0
time_start = time.ticks_ms()
last_frame_count = 0

while True:

    gen_start = time.ticks_ms()
    fbuf.fill(0x0000)
    font.write("Some text", fbuf, framebuf.RGB565, fbuf_width, fbuf_height, 60, 120, color, rot=angle, x_spacing=0, y_spacing=0)

    gen_end = time.ticks_ms()

    print(f'Gen time: {gen_end - gen_start} ms')

    angle += 3
    
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


