import pygame
import os
import numpy as np
from PIL import Image

pygame.init()

fonts = {
    'vga1_bold_16x32': {'image': Image.open('fonts/vga1_bold_16x32.png'), 'width': 16, 'height': 32},
    'vga2_8x16': {'image': Image.open('fonts/vga2_8x16.png'), 'width': 8, 'height': 16},
    'vga2_bold_16x32': {'image': Image.open('fonts/vga2_bold_16x32.png'), 'width': 16, 'height': 32}
}

def get_vga_text(font, string):
    width = fonts[font]['width']
    height = fonts[font]['height']
    map_image = fonts[font]['image']
    character_images = []
    for character in string:
        x = (ord(character)*width)+width
        y = (ord(character)*height)+height
        character_images.append(map_image.crop(x, y, width, height))
    total_width = width*len(string)
    image = Image.new('RGB', (total_width, height))
    x = 0
    for character_image in character_images:
        image.paste(character_image, (x, 0))
        x += width

class GUI:
    def __init__(self):
        self.display = pygame.display.set_mode((560, 1060))
        self.board_texture = pygame.image.load('board_render.png')
        self.running = True
        self.screen1 = pygame.Surface((240, 240))
        self.screen2 = pygame.Surface((240, 240))
        self.button_states = [0, 0, 0, 0, 0]
        self.iox_button_map = [
            1 << 10, # 0000 0100 0000 0000
            1 << 9,  # 0000 0010 0000 0000
            1 << 8,  # 0000 0001 0000 0000
            1 << 1,  # 0000 0000 0000 0010
            1 << 2,  # 0000 0000 0000 0100
        ]
    
    def rgb565_to_rgb(self, color):
        r = (color & 0xF800) >> 8
        g = (color & 0x07E0) >> 3
        b = (color & 0x001F) << 3
        return (r, g, b)

    def handle_command(self, command):
        screens = [self.screen1, self.screen2]
        if command['module'] == 'gc9a01':
            if command['command'] == 'fill':
                screens[command['parameters']['display']-1].fill(self.rgb565_to_rgb(command['parameters']['color']))
            elif command['command'] == 'pixel':
                screens[command['parameters']['display']-1].set_at(
                    (
                        (command['parameters']['x']),
                        (command['parameters']['y'])
                    ),
                    self.rgb565_to_rgb(command['parameters']['color'])
                )
            elif command['command'] == 'circle':
                pygame.draw.circle(
                    screens[command['parameters']['display']-1],
                    self.rgb565_to_rgb(command['parameters']['color']),
                    (command['parameters']['x'], command['parameters']['y']),
                    command['parameters']['r'],
                    draw_top_left=True,
                    width=1
                )
            elif command['command'] == 'fill_circle':
                pygame.draw.circle(
                    screens[command['parameters']['display']-1],
                    self.rgb565_to_rgb(command['parameters']['color']),
                    (command['parameters']['x'], command['parameters']['y']),
                    command['parameters']['r'],
                    draw_top_left=True
                )
            elif command['command'] == 'fill_rect':
                pygame.draw.rect(
                    screens[command['parameters']['display']-1],
                    self.rgb565_to_rgb(command['parameters']['color']),
                    pygame.Rect(
                        command['parameters']['x'],
                        command['parameters']['y'],
                        command['parameters']['w'],
                        command['parameters']['h']
                    )
                )
            elif command['command'] == 'line':
                pygame.draw.line(
                    screens[command['parameters']['display']-1],
                    self.rgb565_to_rgb(command['parameters']['color']),
                    (
                        command['parameters']['x0'],
                        command['parameters']['y0'],
                    ),
                    (
                        command['parameters']['x1'],
                        command['parameters']['y1'],
                    )
                )
            elif command['command'] == 'write':
                if command['parameters']['font'] == 'fonts.arial32px':
                    font = pygame.font.Font('arial.ttf', 32)
                elif command['parameters']['font'] == 'fonts.arial16px':
                    font = pygame.font.Font('arial.ttf', 16)

                # Render the text into an image
                text_surface = font.render(
                    command['parameters']['string'],
                    True,
                    self.rgb565_to_rgb(command['parameters']['fg_color']),
                    self.rgb565_to_rgb(command['parameters']['bg_color'])
                )
                screens[command['parameters']['display']-1].blit(
                    text_surface,
                    (
                        command['parameters']['x'],
                        command['parameters']['y']
                    )
                )
            elif command['command'] == 'text':
                raw_str = get_vga_text(command['parameters']['font'], command['parameters']['string']).tobytes("raw", 'RGBA')
                text = pygame.image.fromstring(raw_str, size, 'RGBA')
                screens[command['parameters']['display']-1].blit(
                    text,
                    (
                        command['parameters']['x'],
                        command['parameters']['y']
                    )
                )
            elif command['command'] == 'write_len':
                if command['parameters']['font'] == 'fonts.arial32px':
                    font = pygame.font.Font('arial.ttf', 32)
                elif command['parameters']['font'] == 'fonts.arial16px':
                    font = pygame.font.Font('arial.ttf', 16)
                
                text_surface = font.render(
                    command['parameters']['string'],
                    True,
                    (255, 255, 255)
                )

                return text_surface.get_width()
            elif command['command'] == 'jpg':
                img = pygame.image.load(
                    os.path.join('src', command['parameters']['filename'])
                )
                screens[command['parameters']['display']-1].blit(
                    img,
                    (
                        command['parameters']['x'],
                        command['parameters']['y']
                    )
                )
        elif command['module'] == 'pca9535':
            if command['command'] == 'get_inputs':
                #print(self.button_states)
                #print(self.get_inputs(self.button_states))
                return self.get_inputs(self.button_states)

    def get_inputs(self, input_list):
        input_number = 1798
        for index, button in enumerate(input_list):
            if button:
                input_number -= self.iox_button_map[index]
        
        return input_number

    def generate_circular_cutout(self, surface):
        circle_mask = pygame.Surface((240, 240), pygame.SRCALPHA)
        circle_mask.fill((0, 0, 0, 0))
        pygame.draw.circle(
            circle_mask, 
            (255, 255, 255, 255),
            (240 // 2, 240 // 2),
            240 // 2
        )

        circular_cutout = pygame.Surface((240, 240), pygame.SRCALPHA)
        circular_cutout.fill((0, 0, 0, 0))
        circular_cutout.blit(
            surface, 
            (0, 0), 
            area=pygame.Rect(0, 0, 240, 240)
        )

        circular_cutout.blit(circle_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        return circular_cutout

    def gameloop(self):
        while self.running:
            self.display.blit(self.generate_circular_cutout(self.screen1), (70, 558))
            self.display.blit(self.generate_circular_cutout(self.screen2), (234, 774))
            self.display.blit(self.board_texture, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.button_states[0] = 1
                    elif event.key == pygame.K_2:
                        self.button_states[1] = 1
                    elif event.key == pygame.K_3:
                        self.button_states[2] = 1
                    elif event.key == pygame.K_4:
                        self.button_states[3] = 1
                    elif event.key == pygame.K_5:
                        self.button_states[4] = 1
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_1:
                        self.button_states[0] = 0
                    elif event.key == pygame.K_2:
                        self.button_states[1] = 0
                    elif event.key == pygame.K_3:
                        self.button_states[2] = 0
                    elif event.key == pygame.K_4:
                        self.button_states[3] = 0
                    elif event.key == pygame.K_5:
                        self.button_states[4] = 0

            pygame.display.update()
