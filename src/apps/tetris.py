import asyncio

import micropython

import time
from apps.app import BaseApp
import random
import vga2_bold_16x32 as font 
import vga2_8x16 as font_small 
import framebuf

from single_app_runner import run_app
from drivers.displays import rgb
import gc9a01


@micropython.viper
def swap16(buf: ptr8, n: int):
    for i in range(n):
        t         = buf[i*2]
        buf[i*2]  = buf[i*2+1]
        buf[i*2+1]= t


class View(BaseApp):
    """
    Tetris
    """

    name = "Tetris"
    def __init__(self, controller):
        super().__init__(controller)
        self.controller.neopixel.fill((0, 0, 0))
        self.controller.neopixel.write()
        displays = self.controller.displays
        black = displays.COLOR_LOOKUP['fbuf']['black']
        displays.display1.fill(black)
        displays.display2.fill(black)
        self.rows = 20
        self.columns = 10
        self.block_size = 10
        self.next_block_size = 20
        self.score = 0
        self.lines = 0
        controller.bsp.speaker.start_song('tetris', repeat=True)
        self.grid = [[0 for column in range(self.columns)] for row in range(self.rows)]
        self.blocks = [
            [
                [1, 1, 1],
                [0, 1, 0]
            ],
            [
                [1, 1, 1, 1]
            ],
            [
                [0, 1, 1],
                [1, 1, 0]
            ],
            [
                [1, 1, 0],
                [0, 1, 1]
            ],
            [
                [1, 1, 1],
                [0, 0, 1]
            ],
            [
                [1, 1, 1],
                [1, 0, 0]
            ],
            [
                [1, 1],
                [1, 1]
            ]
        ]

        self.current_block = None
        self.is_game_over = False

        self.display1_mem_buf = bytearray(240*240*2)
        self.display1_fbuf_mv = memoryview(self.display1_mem_buf)
        self.display1_fbuf = framebuf.FrameBuffer(
            self.display1_mem_buf, 
            240, 
            240, 
            framebuf.RGB565
        )

        x_offset = round((self.controller.displays.display1.width() - (self.columns * self.block_size)) / 2)
        y_offset = round((self.controller.displays.display1.height() - (self.rows * self.block_size)) / 2)

        self.display1_fbuf.fill_rect(
            x_offset-5, 
            y_offset-5, 
            (self.columns * self.block_size)+10, 
            (self.rows * self.block_size)+10, 
            rgb((20, 20, 20))
        )
        self.next_block = random.choice(self.blocks)

        self.add_block()

    def button_press(self, button):
        if self.is_game_over:
            if button == 6:
                self.__init__(self.controller)
            return
        if button == 5:
            # Move left
            self.move_block_horizontal(-1)
            self.draw_scene()
        elif button == 4:
            # Move right
            self.move_block_horizontal(1)
            self.draw_scene()
    
    def button_click(self, button):
        if button == 6:
            # Rotate block and immediately redraw
            self.rotate_current_block()
            self.draw_scene()

    def button_long_press(self, button):
        if button == 6:
            # Drop the current block all the way down
            self.drop_current_block()
            self.draw_scene()

    def update_stats(self):
        displays = self.controller.displays
        black = displays.COLOR_LOOKUP['gc9a01']['black']
        white = displays.COLOR_LOOKUP['gc9a01']['white']
        red = displays.COLOR_LOOKUP['gc9a01']['red']
        self.controller.displays.display2.fill(black)
        if not self.is_game_over:
            x = round(self.controller.displays.display2.width()/4)
            y = 60
            self.controller.displays.display2.fill_rect(
                x-5, 
                y-5, 
                (len(self.next_block[0]) * self.next_block_size)+10, 
                (len(self.next_block) * self.next_block_size)+10, 
                gc9a01.color565(20, 20, 20)
            )
            for row_number, row in enumerate(self.next_block):
                for column_number, cell in enumerate(row):
                    if cell:
                        self.controller.displays.display2.fill_rect(x, y, self.next_block_size, self.next_block_size, red)
                    else:
                        self.controller.displays.display2.fill_rect(x, y, self.next_block_size, self.next_block_size, black)
                    x += self.next_block_size
                x = round(self.controller.displays.display2.width()/4)
                y += self.next_block_size
            self.controller.displays.display2.text(
                font_small,
                "Next",
                round(self.controller.displays.display2.width()/4),
                60 - font_small.HEIGHT,
                white,
                black
            )
        self.controller.displays.display2.text(
            font_small,
            f"Score: {self.score}",
            round(self.controller.displays.display2.width()/4),
            120,
            white,
            black
        )
        self.controller.displays.display2.text(
            font_small,
            f"Lines: {self.lines}",
            round(self.controller.displays.display2.width()/4),
            120 + font_small.HEIGHT,
            white,
            black
        )

    def add_block(self):
        block_width = len(self.next_block[0])
        x = round(self.columns/2 - block_width/2)
        y = 0

        self.current_block = {
            'x': x,
            'y': y,
            'block': self.next_block
        }

        if self.collision(x, y, self.next_block):
            self.is_game_over = True
            return

        self.place_block_in_grid(self.current_block, 1)
        self.next_block = random.choice(self.blocks)
        self.update_stats()

    def place_block_in_grid(self, block_info, value):
        bx = block_info['x']
        by = block_info['y']
        shape = block_info['block']
        for row in shape:
            tx = bx
            for cell in row:
                if cell:
                    self.grid[by][tx] = value
                tx += 1
            by += 1

    def collision(self, x, y, block_shape):
        block_height = len(block_shape)
        block_width = len(block_shape[0])
        for row_i in range(block_height):
            for col_i in range(block_width):
                if block_shape[row_i][col_i] == 1:
                    if (y + row_i) < 0 or (y + row_i) >= self.rows:
                        return True
                    if (x + col_i) < 0 or (x + col_i) >= self.columns:
                        return True
                    if self.grid[y + row_i][x + col_i] == 1:
                        return True
        return False

    def compute_drop_y(self, block_info):
        shape = block_info['block']
        x = block_info['x']
        y = block_info['y']
        while True:
            test_y = y + 1
            if test_y + len(shape) > self.rows or self.collision(x, test_y, shape):
                return y
            y = test_y

    def rotate_current_block(self):
        if not self.current_block or self.is_game_over:
            return
        self.place_block_in_grid(self.current_block, 0)
        old_shape = self.current_block['block']
        rotated = list(zip(*old_shape[::-1]))
        rotated = [list(row) for row in rotated]

        x = self.current_block['x']
        y = self.current_block['y']
        if self.collision(x, y, rotated):
            self.place_block_in_grid(self.current_block, 1)
        else:
            self.current_block['block'] = rotated
            self.place_block_in_grid(self.current_block, 1)

    def move_block_horizontal(self, dx):
        if not self.current_block or self.is_game_over:
            return
        self.place_block_in_grid(self.current_block, 0)
        x = self.current_block['x']
        y = self.current_block['y']
        shape = self.current_block['block']
        new_x = x + dx
        if self.collision(new_x, y, shape):
            self.place_block_in_grid(self.current_block, 1)
        else:
            self.current_block['x'] = new_x
            self.place_block_in_grid(self.current_block, 1)

    def drop_current_block(self):
        if not self.current_block or self.is_game_over:
            return
        self.place_block_in_grid(self.current_block, 0)
        while True:
            x = self.current_block['x']
            y = self.current_block['y']
            shape = self.current_block['block']
            new_y = y + 1
            if new_y + len(shape) > self.rows or self.collision(x, new_y, shape):
                self.place_block_in_grid(self.current_block, 1)
                self.clear_full_lines()
                self.add_block()
                break
            else:
                self.current_block['y'] = new_y

    def move_block_down(self):
        if not self.current_block or self.is_game_over:
            return
        self.place_block_in_grid(self.current_block, 0)
        x = self.current_block['x']
        y = self.current_block['y']
        shape = self.current_block['block']
        new_y = y + 1
        if new_y + len(shape) > self.rows:
            self.place_block_in_grid(self.current_block, 1)
            self.clear_full_lines()
            self.add_block()
            return
        if self.collision(x, new_y, shape):
            self.place_block_in_grid(self.current_block, 1)
            self.clear_full_lines()
            self.add_block()
        else:
            self.current_block['y'] = new_y
            self.place_block_in_grid(self.current_block, 1)

    def clear_full_lines(self):
        new_grid = []
        lines_just_cleared = 0
        for row in self.grid:
            if all(cell == 1 for cell in row):
                lines_just_cleared += 1
            else:
                new_grid.append(row)

        for _ in range(lines_just_cleared):
            new_grid.insert(0, [0]*self.columns)

        self.grid = new_grid
        self.lines += lines_just_cleared
        if lines_just_cleared == 1:
            self.score += 40
        elif lines_just_cleared == 2:
            self.score += 100
        elif lines_just_cleared == 3:
            self.score += 300
        elif lines_just_cleared == 4:
            self.score += 1200

    def draw_scene(self):
        if self.current_block:
            self.place_block_in_grid(self.current_block, 0)
            ghost_y = self.compute_drop_y(self.current_block)
            self.place_block_in_grid(self.current_block, 1)
        else:
            ghost_y = 0

        displays = self.controller.displays
        disp = displays.display1

        red = displays.COLOR_LOOKUP['fbuf']['red']
        black = displays.COLOR_LOOKUP['fbuf']['black']

        x_offset = round((disp.width() - (self.columns * self.block_size)) / 2)
        y_offset = round((disp.height() - (self.rows * self.block_size)) / 2)

        y_pix = y_offset
        for row in self.grid:
            x_pix = x_offset
            for cell in row:
                if cell:
                    self.display1_fbuf.fill_rect(x_pix, y_pix, self.block_size, self.block_size, red)
                else:
                    self.display1_fbuf.fill_rect(x_pix, y_pix, self.block_size, self.block_size, black)
                x_pix += self.block_size
            y_pix += self.block_size

        
        if self.current_block:
            # draw the ghost
            shape = self.current_block['block']
            gx = self.current_block['x']
            for row_i, row in enumerate(shape):
                for col_i, cell in enumerate(row):
                    if cell:
                        pixel_x = x_offset + (gx + col_i) * self.block_size
                        pixel_y = y_offset + (ghost_y + row_i) * self.block_size
                        self.display1_fbuf.fill_rect(pixel_x, pixel_y, self.block_size, self.block_size, 0x78)

        self.controller.displays.display1.blit_buffer(self.display1_fbuf_mv, 0, 0, 240, 240)

    async def update(self):
        debug = False
        t_start = time.time_ns()
        if self.is_game_over:
            await self.game_over()
            return
        y_offset = round((self.controller.displays.display1.height() - (self.rows * self.block_size)) / 2)+(self.rows * self.block_size)+5
        x_offset = round((self.controller.displays.display1.width() - (self.columns * self.block_size)) / 2)
        self.display1_fbuf.fill_rect(x_offset-5, y_offset-10, self.controller.displays.display1.width(), 5, rgb((20, 20, 20)))
        self.display1_fbuf.fill_rect(0, y_offset, self.controller.displays.display1.width(), self.controller.displays.display1.height()-y_offset, rgb((0, 0, 0)))
        t1 = time.time_ns()
        self.draw_scene()
        t2 = time.time_ns()
        self.move_block_down()

        t_end = time.time_ns()
        total_time_s = (t_end - t_start)/1_000_000_000
        if debug:
            print(f"Update time: {(t_end - t_start)/1_000_000} ms, Draw time: {(t2 - t1)/1_000_000} ms, Move time: {(t_end - t2)/1_000_000} ms")
        
        # If the render gets delayed, we will take that into account when we sleep
        await asyncio.sleep(0.5 - total_time_s)

    async def game_over(self):
        black = self.controller.displays.COLOR_LOOKUP['gc9a01']['black']
        red = self.controller.displays.COLOR_LOOKUP['gc9a01']['red']
        self.controller.neopixel.fill((40, 0, 0))
        self.controller.neopixel.write()
        self.controller.displays.display1.fill(black)
        self.controller.displays.display_center_text(
            "Game Over", 
            red, 
            black, 
            1, 
            font)
        self.controller.displays.display1.text(
            font_small,
            "SEL to retry",
            int((self.controller.displays.display1.width()/2) - ((font_small.WIDTH*len("SEL to retry")/2))),
            int((self.controller.displays.display1.height()/2) - (font_small.HEIGHT/2)) + font_small.HEIGHT*2,
            red,
            black
        )
        self.update_stats()
        while self.is_game_over:
            await asyncio.sleep(0.05)

if __name__ == "__main__":
    run_app(View, perf=True)