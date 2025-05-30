import framebuf
import time

USE_PY_DRIVER = True
if USE_PY_DRIVER:
    from drivers.gc9a01 import GC9A01
else:
    from gc9a01 import GC9A01


if __name__ == "__main__":
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
    spi = SPI(1, baudrate=machine.freq() // 2, sck=Pin(SCK), mosi=Pin(MOSI))

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
    )
    display.fill_rect(0, 0, 240, 240, 0xF800)

    mem_buf_1 = bytearray(240*240*2)
    mem_buf_2 = bytearray(240*240*2)
    fbuf_mem_1 = memoryview(mem_buf_1)
    fbuf_mem_2 = memoryview(mem_buf_2)
    fbuf_1 = framebuf.FrameBuffer(
        fbuf_mem_1, 
        240, 
        240, 
        framebuf.RGB565
    )
    fbuf_2 = framebuf.FrameBuffer(
        fbuf_mem_2, 
        240, 
        240, 
        framebuf.RGB565
    )

    from img import bsides_logo

    def use_fbuf():
        while True:
            for i in range(0, 0xFFFF):
                t_start = time.time_ns()
                fbuf = fbuf_1
                fbuf_mem = mem_buf_1
                # if i % 2 == 0:
                #     fbuf = fbuf_1
                #     fbuf_mem = mem_buf_1
                # else:
                #     fbuf = fbuf_2
                #     fbuf_mem = mem_buf_2

                fbuf.fill_rect(
                    0,
                    0,
                    240,
                    240,
                    i
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
    
    def use_display_methods():
        while True:
            for i in range(0, 0xFFFF):
                t_start = time.time_ns()
                # display.fill_rect(0, 0, 240, 240, i)
                display.bitmap(
                    bsides_logo,
                    0,
                    0
                )
                t_end = time.time_ns()
                elapsed_time = (t_end - t_start) / 1_000_000
                print(f"Elapsed time: {elapsed_time:.2f} ms")
    
    use_display_methods()
    # use_fbuf()

