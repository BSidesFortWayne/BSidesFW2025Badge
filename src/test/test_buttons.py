import framebuf
import time

from bsp import BSP
from hardware_rev import HardwareRev

bsp = BSP(hardware_version=HardwareRev.V3)

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

mv = memoryview(mem_buf)

frame_count = 0
time_start = time.ticks_ms()
last_frame_count= 0
buttons = bsp.buttons

indicator_width = 20
indicator_height = 20

padding = 5

total_width = indicator_width * len(buttons) + padding * (len(buttons) - 1)
total_height = indicator_height * 3 + padding * 2
offset_x = (fbuf_width - total_width) // 2
offset_y = (fbuf_height - total_height) // 2
offset_y -= 20

text_offset = 20
start_time = 0

leds = bsp.leds

def rgb(color: tuple):
    r,g,b = color
    return (r & 0xF8) | ((g & 0xE0) >> 5) | ((g & 0x1C) << 11) | ((b & 0xF8) << 5)


released_color = (255, 0, 0)
pressed_color = (0, 255, 0)
long_pressed_color = (0, 0, 255)

state_to_color = {
    "Released": released_color,
    "Pressed": pressed_color,
    "Long Pressed": long_pressed_color,
}

while True:

    gen_start = time.ticks_ms()
    fbuf.fill(0x0000)

    y = offset_y
    y_increment = indicator_height + padding
    
    # Draw first column with text for each button
    fbuf.text("B",  offset_x - text_offset, y, 0xFFFF)
    fbuf.text("LP", offset_x - text_offset, y+y_increment + 6, 0xFFFF)
    fbuf.text("P",  offset_x - text_offset, y+y_increment*2 + 6, 0xFFFF)
    fbuf.text("R",  offset_x - text_offset, y+y_increment*3 + 6, 0xFFFF)

    any_pressed = False
    for i,state in enumerate(buttons):
        # Check if any button is pressed
        if state == "Pressed" or state == "Long Pressed":
            any_pressed = True

        x = offset_x + i * (indicator_width + padding)

        # Draw button number as column header
        fbuf.text(str(i), x + 5, y, 0xFFFF)

        leds.set_led_color(i, state_to_color[state])
        
        # Draw first row as a circle and fill if "Long Pressed"\
        method = fbuf.fill_rect if state == "Long Pressed" else fbuf.rect
        method(
            x, 
            y+y_increment, 
            indicator_width, 
            indicator_height, 
            rgb(long_pressed_color)
        )

        # Draw second row as a circle and fill if "Pressed" or "Long Pressed"
        method = fbuf.fill_rect if state == "Pressed" else fbuf.rect
        method(
            x, 
            y+y_increment*2, 
            indicator_width, 
            indicator_height, 
            rgb(pressed_color)
        )

        # Draw third row as a circle and fill if "Released"
        method = fbuf.fill_rect if state == "Released" else fbuf.rect
        method(
            x, 
            y+y_increment*3, 
            indicator_width, 
            indicator_height, 
            rgb(released_color)
        )
    
    if any_pressed:
        if not start_time:
            start_time = time.ticks_ms()
        elapsed = time.ticks_diff(time.ticks_ms(), start_time)
        fbuf.text(
            f"Elapsed: {round(elapsed / 1000, 1)} s",
            offset_x,
            offset_y - text_offset,
            0xFFFF
        )
    else:
        start_time = 0

    gen_end = time.ticks_ms()
    
    bsp.displays.display1.blit_buffer(
        mv,
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


