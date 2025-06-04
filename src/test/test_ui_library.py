import framebuf
import time

from ui.menu import TextMenuWidget
from ui.table_layout import TableLayout
from ui.common import Direction
from ui.stack_layout import StackLayout
from ui.text_box import TextBox
from ui.absolute_layout import AbsoluteLayout

USE_PY_DRIVER = True
if USE_PY_DRIVER:
    from drivers.gc9a01 import GC9A01
else:
    from gc9a01 import GC9A01


import machine
import time
from machine import Pin, SPI

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

# Example 1: Absolute Layout + StackLayout
# layout = AbsoluteLayout(
#     StackLayout(
#         TextBox(height=20, width=100, text="Hello"),
#         TextBox(height=20, width=100, text="World"),
#         spacing=10,
#         direction=Direction.HORIZONTAL
#     ), 
#     0, 
#     0,
# )

# Example 2: StackLayout with AbsoluteLayout
# layout = AbsoluteLayout(
#     AbsoluteLayout(
#         TextBox(height=20,width=100,text="Hello"), 40, 40,
#         TextBox(height=20,width=100,text="World"), 40, 80,
#     ), 
#     0, 
#     0
# )

# Example 3: TableLayout
# layout = AbsoluteLayout(
#     TableLayout(
#         ["R1C1", "R1C2", "R1C3"], # , "R1C4"],
#         ["R2C1", "R2C2", "R2C3"], # , "R2C4"],
#         ["R3C1", "R3C2", "R3C3"], # , "R3C4"],
#         ["R4C1", "R4C2", "R4C3"], # , "R4C4"],
#         padding=5,
#         cell_highlight=(3, 2),
#     ),
#     30,
#     40
# )

# Example 4: Menu
layout = AbsoluteLayout(
    TextMenuWidget(
        {
            "Item 1": "Description 1",
            "Item 2": {
                "Sub Item 1": "Sub Description 1",
                "Sub Item 2": "Sub Description 2",
                "Sub Item 3": {
                    "Deep Sub Item 1": "Deep Sub Description 1",
                    "Deep Sub Item 2": "Deep Sub Description 2",
                },
            },
            "Item 3": "Description 3",
            "Item 4": {
                "Sub Item 1": "Sub Description 1",
                "Sub Item 2": "Sub Description 2",
            },
        },
        title="Menu Example",
        path=["Item 2"]
    ),
    40,
    40
)

step = 3
while True:
    t_start = time.time_ns()

    fbuf.fill(0x0000)
    # layout.children[0].x += step
    # layout.children[0].y += step
    # layout.children[0].x %= 240
    # layout.children[0].y %= 240
    layout.render(
        0,
        0,
        fbuf,
        240,
        240
    )

    display.blit_buffer(
        fbuf_mem,
        0,
        0,
        240,
        240
    )
    t_end = time.time_ns()
    elapsed_time = (t_end - t_start) / 1_000_000
    time.sleep_ms(20)
    print(f"Elapsed time: {elapsed_time:.2f} ms")
