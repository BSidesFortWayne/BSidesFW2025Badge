import apps.view
import random
import time
from main import Controller
import vga2_bold_16x32 as font # type: ignore
import vga2_8x16 as font_small # type: ignore
import audio
import _thread

class View(apps.view.View):
    """
    Tetris

    V1:

    SW4 - Drop
    SW3 - Rotate
    SW2 - Right
    SW1 - Left

    V2:

    SW3 - Rotate
    SW5 - Right
    SW6 - Left
    SW4 - Drop
    """

    def __init__(self, controller):
        self.controller = controller
        self.controller.neopixel.fill((0, 0, 0))
        self.controller.neopixel.write()
        self.controller.displays.display1.fill(self.controller.displays.gc9a01.BLACK)
        self.controller.displays.display2.fill(self.controller.displays.gc9a01.BLACK)
        self.rows = 20
        self.columns = 10
        self.block_size = 10
        self.next_block_size = 20
        self.score = 0
        self.lines = 0
        controller.bsp.speaker.start_tetris()
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

        x_offset = round((self.controller.displays.display1.width() - (self.columns * self.block_size)) / 2)
        y_offset = round((self.controller.displays.display1.height() - (self.rows * self.block_size)) / 2)

        self.controller.displays.display1.fill_rect(x_offset-5, y_offset-5, (self.columns * self.block_size)+10, (self.rows * self.block_size)+10, self.controller.displays.gc9a01.color565(20, 20, 20))
        self.next_block = random.choice(self.blocks)

        self.add_block()

    def button_press(self, button):
        if self.is_game_over:
            if button == 2:
                self.__init__(self.controller)
            return
        if self.controller.bsp.hardware_version == 1:
            if button == 1:
                # Move left
                self.move_block_horizontal(-1)
                self.draw_scene()
            elif button == 2:
                # Move right
                self.move_block_horizontal(1)
                self.draw_scene()
            elif button == 4:
                # Drop the current block all the way down
                self.drop_current_block()
                self.draw_scene()
            elif button == 3:
                # Rotate block and immediately redraw
                self.rotate_current_block()
                self.draw_scene()
        else:
            if button == 6:
                # Move left
                self.move_block_horizontal(-1)
                self.draw_scene()
            elif button == 5:
                # Move right
                self.move_block_horizontal(1)
                self.draw_scene()
            elif button == 4:
                # Drop the current block all the way down
                self.drop_current_block()
                self.draw_scene()
            elif button == 3:
                # Rotate block and immediately redraw
                self.rotate_current_block()
                self.draw_scene()

    def update_stats(self):
        self.controller.displays.display2.fill(self.controller.displays.gc9a01.BLACK)
        if not self.is_game_over:
            x = round(self.controller.displays.display2.width()/4)
            y = 60
            self.controller.displays.display2.fill_rect(x-5, y-5, (len(self.next_block[0]) * self.next_block_size)+10, (len(self.next_block) * self.next_block_size)+10, self.controller.displays.gc9a01.color565(20, 20, 20))
            for row_number, row in enumerate(self.next_block):
                for column_number, cell in enumerate(row):
                    if cell:
                        self.controller.displays.display2.fill_rect(x, y, self.next_block_size, self.next_block_size, self.controller.displays.gc9a01.RED)
                    else:
                        self.controller.displays.display2.fill_rect(x, y, self.next_block_size, self.next_block_size, self.controller.displays.gc9a01.BLACK)
                    x += self.next_block_size
                x = round(self.controller.displays.display2.width()/4)
                y += self.next_block_size
            self.controller.displays.display2.text(
                font_small,
                "Next",
                round(self.controller.displays.display2.width()/4),
                60 - font_small.HEIGHT,
                self.controller.displays.gc9a01.WHITE,
                self.controller.displays.gc9a01.BLACK
            )
        self.controller.displays.display2.text(
            font_small,
            f"Score: {self.score}",
            round(self.controller.displays.display2.width()/4),
            120,
            self.controller.displays.gc9a01.WHITE,
            self.controller.displays.gc9a01.BLACK
        )
        self.controller.displays.display2.text(
            font_small,
            f"Lines: {self.lines}",
            round(self.controller.displays.display2.width()/4),
            120 + font_small.HEIGHT,
            self.controller.displays.gc9a01.WHITE,
            self.controller.displays.gc9a01.BLACK
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

        disp = self.controller.displays.display1
        gc9a01 = self.controller.displays.gc9a01

        x_offset = round((disp.width() - (self.columns * self.block_size)) / 2)
        y_offset = round((disp.height() - (self.rows * self.block_size)) / 2)

        y_pix = y_offset
        for row in self.grid:
            x_pix = x_offset
            for cell in row:
                if cell:
                    disp.fill_rect(x_pix, y_pix, self.block_size, self.block_size, gc9a01.RED)
                else:
                    disp.fill_rect(x_pix, y_pix, self.block_size, self.block_size, gc9a01.BLACK)
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
                        disp.fill_rect(pixel_x, pixel_y, self.block_size, self.block_size, 0x7800)

    def update(self):
        if self.is_game_over:
            self.game_over()
            return
        y_offset = round((self.controller.displays.display1.height() - (self.rows * self.block_size)) / 2)+(self.rows * self.block_size)+5
        x_offset = round((self.controller.displays.display1.width() - (self.columns * self.block_size)) / 2)
        self.controller.displays.display1.fill_rect(x_offset-5, y_offset-10, self.controller.displays.display1.width(), 5, self.controller.displays.gc9a01.color565(20, 20, 20))
        self.controller.displays.display1.fill_rect(0, y_offset, self.controller.displays.display1.width(), self.controller.displays.display1.height()-y_offset, self.controller.displays.gc9a01.BLACK)
        self.draw_scene()
        self.move_block_down()
        time.sleep(0.5)

    def game_over(self):
        self.controller.neopixel.fill((40, 0, 0))
        self.controller.neopixel.write()
        self.controller.displays.display1.fill(self.controller.displays.gc9a01.BLACK)
        self.controller.displays.display_center_text(
            "Game Over", 
            self.controller.displays.gc9a01.RED, 
            self.controller.displays.gc9a01.BLACK, 
            1, 
            font)
        self.controller.displays.display1.text(
            font_small,
            "SW2 to retry",
            int((self.controller.displays.display1.width()/2) - ((font_small.WIDTH*len("SW2 to retry")/2))),
            int((self.controller.displays.display1.height()/2) - (font_small.HEIGHT/2)) + font_small.HEIGHT*2,
            self.controller.displays.gc9a01.RED,
            self.controller.displays.gc9a01.BLACK
        )
        self.update_stats()
        while self.is_game_over:
            time.sleep(0.05)
