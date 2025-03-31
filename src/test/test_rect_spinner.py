import gc9a01
from controller import Controller
import framebuf
import time


c = Controller()

c.bsp.displays.display1.fill(0x000000)

frame_count = 0
last_frame_count = 0

square_side = 50
width = square_side
height = square_side
padding = 20
display_center_x = c.bsp.displays.display1.width() // 2
display_center_y = c.bsp.displays.display1.height() // 2
x = display_center_x - (width + padding // 2)
y = display_center_y - (height + padding // 2)

fbuf_width = 2*width + padding
fbuf_height = 2*height + padding
mem_buf = bytearray(fbuf_width * fbuf_height * 2)

fbuf = framebuf.FrameBuffer(
    mem_buf, 
    fbuf_width,
    fbuf_height,
    framebuf.RGB565
)

def fade_color_to_black(color565: int, step: int):
    r = (color565 & 0xF800) >> 11
    g = (color565 & 0x07E0) >> 5
    b = color565 & 0x001F

    r = r * step // 255
    g = g * step // 255
    b = b * step // 255

    return (r << 11) | (g << 5) | b

def fade_color_to_white(color565: int, step: int):
    r = (color565 & 0xF800) >> 11
    g = (color565 & 0x07E0) >> 5
    b = color565 & 0x001F

    r = r + (255 - r) * step // 255
    g = g + (255 - g) * step // 255
    b = b + (255 - b) * step // 255

    return (r << 11) | (g << 5) | b

def fade_black_to_color(color565: int, step: int):
    r = (color565 & 0xF800) >> 11
    g = (color565 & 0x07E0) >> 5
    b = color565 & 0x001F

    r = r + (0 - r) * step // 255
    g = g + (0 - g) * step // 255
    b = b + (0 - b) * step // 255

    return (r << 11) | (g << 5) | b

# Scale 565 color with percent
def fade_color(percent: float, color: int):
    r = (color & 0xF800) >> 8
    g = (color & 0x07E0) >> 3
    b = (color & 0x001F) << 3

    r = int(r * percent)
    g = int(g * percent)
    b = int(b * percent)

    return (r << 8) | (g << 3) | (b >> 3)

def draw_rect(x, y, color):
    fbuf.fill_rect(x, y, width, height, color)

c.bsp.displays.display1.fill(gc9a01.BLACK)

def rgb_to_565(r, g, b):
    return (r & 0xF8) | ((g & 0xE0) >> 5) | ((g & 0x1C) << 11) | ((b & 0xF8) << 5)

def _565_to_rgb(color565):
    r = (color565 & 0xF800) >> 11
    g = (color565 & 0x07E0) >> 5
    b = color565 & 0x001F

    r = (r << 3) | (r >> 2)
    g = (g << 2) | (g >> 4)
    b = (b << 3) | (b >> 2)

    return r, g, b

# Take two 565 colors and interpolate
def smooth_interpolate_color(color1: int, color2: int, step: int):
    r1, g1, b1 = _565_to_rgb(color1)
    r2, g2, b2 = _565_to_rgb(color2)

    r = int(r1 + (r2 - r1) * step / 511)
    g = int(g1 + (g2 - g1) * step / 511)
    b = int(b1 + (b2 - b1) * step / 511)

    return rgb_to_565(r, g, b)

print(x, y, width, height, padding, display_center_x, display_center_y, fbuf_width, fbuf_height)
fade_square = 0
start_fade_ticks = time.ticks_ms()
fade_duration = 1000
square_colors = [
    gc9a01.RED,
    gc9a01.GREEN,
    gc9a01.BLUE,
    gc9a01.YELLOW
]

start_color = square_colors[fade_square]
square_on = True
time_start = time.ticks_ms()
while True:
    fbuf.fill(gc9a01.BLACK)

    # Draw the spinner, display 4 squares with 90 degree rotation
    
    percent_fade = (time.ticks_ms() - start_fade_ticks) / fade_duration
    step = int(511 * percent_fade)
    # We've hit 100%, switch to the next color
    if (percent_fade > 1):
        # Reset timer
        start_fade_ticks = time.ticks_ms()

        # Finalize the current square as the next squares color
        square_colors[fade_square] = square_colors[(fade_square + 1) % 4]

        # Switch to the next square
        fade_square = (fade_square + 1) % 4

        start_color = square_colors[fade_square]
    else:
        square_colors[fade_square] = smooth_interpolate_color(start_color, square_colors[(fade_square + 1) % 4], step)
    
    draw_rect(
        0, 
        0, 
        square_colors[0]
    )
    draw_rect(
        width + padding, 
        0, 
        square_colors[1]
    )
    draw_rect(
        width + padding, 
        width + padding, 
        square_colors[2]
    )
    draw_rect(
        0, 
        width + padding, 
        square_colors[3]
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
