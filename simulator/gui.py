import pygame
import pygame_gui
import os
import numpy as np
from PIL import Image
import random

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
        x = ord(character) * width
        y = 0
        character_images.append(map_image.crop((x, y, x + width, y + height)))
    total_width = width*len(string)
    image = Image.new('RGB', (total_width, height))
    x = 0
    for character_image in character_images:
        image.paste(character_image, (x, 0))
        x += width
    return image

class GUIEnhanced:
    def __init__(self, config=None, logger=None):
        # Store config and logger
        self.config = config or {}
        self.logger = logger
        
        # Get GUI config
        gui_config = self.config.get('gui', {})
        window_title = gui_config.get('window_title', 'BSides FW 2025 Badge Simulator')
        self.show_fps = gui_config.get('show_fps', False)
        self.target_fps = gui_config.get('target_fps', 60)
        
        # Initialize pygame display with extra space for controls and log
        self.control_panel_width = 300
        self.log_panel_height = 250  # Height for log panel
        self.log_panel_collapsed = True  # Start collapsed
        self.total_height = 1060 + self.log_panel_height  # Total height when log panel is shown
        self.display = pygame.display.set_mode((560 + self.control_panel_width, 1060))  # Start with collapsed height
        pygame.display.set_caption(window_title)
        
        # Log buffer for display
        self.log_buffer = []  # List of log messages
        self.max_log_lines = 100  # Keep last 100 log lines
        self.log_scroll_offset = 0
        
        # Initialize pygame_gui manager
        self.ui_manager = pygame_gui.UIManager((560 + self.control_panel_width, self.total_height))
        
        self.board_texture = pygame.image.load('board_render.png')
        self.running = True
        self.screen1 = pygame.Surface((240, 240))
        self.screen2 = pygame.Surface((240, 240))
        
        # Track button states: 0 = not pressed, >0 = timestamp when pressed
        self.button_states = [0, 0, 0, 0, 0, 0, 0, 0]
        
        # Map keyboard keys to button indices
        self.key_to_button = {
            pygame.K_0: 0,  # Boot/Reset button (SW5)
            pygame.K_1: 1,  # SW1 (top)
            pygame.K_2: 2,  # SW2 (top)
            pygame.K_3: 3,  # SW3 (top)
            pygame.K_4: 4,  # SW4 (top)
            pygame.K_7: 5,  # SW7 (game button 1)
            pygame.K_8: 6,  # SW8 (game button 2)
            pygame.K_9: 7,  # SW9 (game button 3)
        }
        
        # V3 hardware PCA9535 button mapping
        self.iox_button_map = [
            1 << 10, # Button 1: SW1
            1 << 9,  # Button 2: SW2
            1 << 8,  # Button 3: SW3
            1 << 0,  # Button 4: SW4
            1 << 1,  # Button 5: SW7
            1 << 2,  # Button 6: SW8
            1 << 3,  # Button 7: SW9
        ]
        
        # LED state (7 RGB LEDs on badge)
        self.leds = [(0, 0, 0)] * 7
        self.show_leds = gui_config.get('show_led_positions', True)
        
        # FPS tracking
        self.clock = pygame.time.Clock()
        self.frame_count = 0
        self.fps_display_font = pygame.font.Font(None, 24)
        
        # Screenshot support
        self.screenshot_dir = 'screenshots'
        os.makedirs(self.screenshot_dir, exist_ok=True)
        self.screenshot_counter = 0
        self.screenshot_include_controls = False  # Default: badge only
        
        # Hardware mock state
        self.accel_data = [0.0, 0.0, 1.0]  # Default: 1g on Z-axis
        self.shake_magnitude = 2.0  # Default shake intensity
        self.adc_voltage = 4.2  # Default battery voltage (fully charged)
        self.resistor_r1 = 100.0  # Top resistor in divider (kΩ)
        self.resistor_r2 = 47.0   # Bottom resistor in divider (kΩ)
        self.wifi_state = 'disconnected'
        self.bluetooth_state = 'disabled'
        self.charge_state = 'not_charging'
        
        # Queue for pending interrupts (pin_num, edge_type)
        self.interrupt_queue = []
        
        # Button click areas (defined as circles: x, y, radius, button_index)
        # These will be drawn and made clickable
        self.button_click_areas = [
            # Top row buttons SW1-SW4
            (404, 78, 15, 1),   # SW2
            (457, 78, 15, 2),    # SW3  
            (511, 78, 15, 3),    # SW4
            (410, 575, 20, 4),   # SW9
            (353, 566, 20, 5),   # SW8
            (46, 481, 20, 6),    # SW7
            (351, 78, 15, 7),    # SW1?
        ]
        
        # Create UI controls
        self._create_ui_controls()
    
    def _create_ui_controls(self):
        """Create the control panel UI elements"""
        panel_x = 570  # Right side of badge display
        y_offset = 20
        spacing = 10
        
        # Title
        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, 280, 30),
            text='Hardware Controls',
            manager=self.ui_manager
        )
        y_offset += 40
        
        # === Accelerometer Section ===
        self.accel_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, 280, 25),
            text='Accelerometer',
            manager=self.ui_manager
        )
        y_offset += 30
        
        # Shake button
        self.shake_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_x, y_offset, 280, 35),
            text='Shake Device',
            manager=self.ui_manager
        )
        y_offset += 40
        
        # Shake magnitude slider
        self.shake_mag_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, 200, 25),
            text=f'Shake Magnitude: {self.shake_magnitude:.1f}g',
            manager=self.ui_manager
        )
        y_offset += 30
        
        self.shake_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(panel_x, y_offset, 280, 25),
            start_value=self.shake_magnitude,
            value_range=(0.5, 8.0),
            manager=self.ui_manager
        )
        y_offset += 35
        
        # Accel X/Y/Z display
        self.accel_display_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, 280, 20),
            text=f'X: {self.accel_data[0]:.2f}g Y: {self.accel_data[1]:.2f}g Z: {self.accel_data[2]:.2f}g',
            manager=self.ui_manager
        )
        y_offset += 30
        
        # === Power/ADC Section ===
        self.power_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, 280, 25),
            text='Power & Battery',
            manager=self.ui_manager
        )
        y_offset += 30
        
        # ADC voltage slider
        self.adc_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, 200, 25),
            text=f'Battery Voltage: {self.adc_voltage:.2f}V',
            manager=self.ui_manager
        )
        y_offset += 30
        
        self.adc_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(panel_x, y_offset, 280, 25),
            start_value=self.adc_voltage,
            value_range=(2.9, 4.5),
            manager=self.ui_manager
        )
        y_offset += 35
        
        # Resistor divider R1 (top resistor)
        self.r1_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, 200, 25),
            text=f'R1 (top): {self.resistor_r1:.1f}kΩ',
            manager=self.ui_manager
        )
        y_offset += 30
        
        self.r1_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(panel_x, y_offset, 280, 25),
            start_value=self.resistor_r1,
            value_range=(10.0, 200.0),
            manager=self.ui_manager
        )
        y_offset += 35
        
        # Resistor divider R2 (bottom resistor)
        self.r2_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, 200, 25),
            text=f'R2 (bottom): {self.resistor_r2:.1f}kΩ',
            manager=self.ui_manager
        )
        y_offset += 30
        
        self.r2_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(panel_x, y_offset, 280, 25),
            start_value=self.resistor_r2,
            value_range=(10.0, 200.0),
            manager=self.ui_manager
        )
        y_offset += 35
        
        # Divided voltage display (what ADC actually sees)
        self.divided_voltage_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, 280, 20),
            text=f'ADC sees: {self._calculate_divided_voltage():.0f}mV',
            manager=self.ui_manager
        )
        y_offset += 30
        
        # Charge state dropdown
        self.charge_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, 200, 25),
            text='Charge State:',
            manager=self.ui_manager
        )
        y_offset += 30
        
        self.charge_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=['not_charging', 'charging', 'charged', 'error'],
            starting_option='not_charging',
            relative_rect=pygame.Rect(panel_x, y_offset, 280, 35),
            manager=self.ui_manager
        )
        y_offset += 45
        
        # === WiFi Section ===
        self.wifi_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, 280, 25),
            text='WiFi',
            manager=self.ui_manager
        )
        y_offset += 30
        
        self.wifi_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=['disconnected', 'connecting', 'connected', 'passthrough', 'ap_mode'],
            starting_option='disconnected',
            relative_rect=pygame.Rect(panel_x, y_offset, 280, 35),
            manager=self.ui_manager
        )
        y_offset += 45
        
        # === Bluetooth Section ===
        self.bluetooth_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, 280, 25),
            text='Bluetooth',
            manager=self.ui_manager
        )
        y_offset += 30
        
        self.bluetooth_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=['disabled', 'advertising', 'connected', 'system_passthrough'],
            starting_option='disabled',
            relative_rect=pygame.Rect(panel_x, y_offset, 280, 35),
            manager=self.ui_manager
        )
        y_offset += 45
        
        # === Screenshot Section ===
        self.screenshot_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_x, y_offset, 280, 40),
            text='Save Screenshot',
            manager=self.ui_manager
        )
        y_offset += 45
        
        self.screenshot_controls_checkbox = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_x, y_offset, 280, 30),
            text='Screenshot Excludes Controls',
            manager=self.ui_manager
        )
        y_offset += 40
        
        # === FPS Display ===
        self.fps_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(panel_x, y_offset, 280, 25),
            text='FPS: --',
            manager=self.ui_manager
        )
        y_offset += 35
        
        # === Info Section ===
        self.info_label = pygame_gui.elements.UITextBox(
            html_text='<font size=2>Press 0-4, 7-9 for buttons<br>Click buttons on badge image<br>Adjust sliders to mock hardware values</font>',
            relative_rect=pygame.Rect(panel_x, y_offset, 280, 100),
            manager=self.ui_manager
        )
        y_offset += 110
        
        # === Log Panel Toggle ===
        self.log_toggle_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(panel_x, y_offset, 280, 35),
            text='Show Log Panel',
            manager=self.ui_manager
        )
    
    def add_log_message(self, message: str, level: str = 'INFO'):
        """Add a message to the log buffer
        
        Args:
            message: Log message text
            level: Log level (INFO, WARNING, ERROR, etc.)
        """
        import datetime
        timestamp = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        log_entry = f'[{timestamp}] {level}: {message}'
        self.log_buffer.append(log_entry)
        
        # Keep buffer size manageable
        if len(self.log_buffer) > self.max_log_lines:
            self.log_buffer = self.log_buffer[-self.max_log_lines:]
            
        # Also print to console
        print(log_entry)
    
    def render_log_panel(self):
        """Render the log panel at the bottom of the window"""
        if self.log_panel_collapsed:
            return
        
        # Log panel background
        log_panel_y = 1060  # Below the main badge display
        log_rect = pygame.Rect(0, log_panel_y, 560 + self.control_panel_width, self.log_panel_height)
        pygame.draw.rect(self.display, (20, 20, 20), log_rect)
        pygame.draw.line(self.display, (100, 100, 100), (0, log_panel_y), (560 + self.control_panel_width, log_panel_y), 2)
        
        # Title
        title_font = pygame.font.Font(None, 24)
        title_surface = title_font.render('Log Output', True, (200, 200, 200))
        self.display.blit(title_surface, (10, log_panel_y + 10))
        
        # Render log messages
        log_font = pygame.font.Font(None, 18)
        line_height = 20
        y = log_panel_y + 40
        visible_lines = (self.log_panel_height - 50) // line_height
        
        # Show most recent messages (bottom of log buffer)
        start_idx = max(0, len(self.log_buffer) - visible_lines - self.log_scroll_offset)
        end_idx = len(self.log_buffer) - self.log_scroll_offset
        
        for log_entry in self.log_buffer[start_idx:end_idx]:
            # Color code by level
            color = (200, 200, 200)  # Default
            if 'ERROR' in log_entry:
                color = (255, 100, 100)
            elif 'WARNING' in log_entry:
                color = (255, 200, 100)
            elif 'INFO' in log_entry:
                color = (150, 200, 255)
            
            # Truncate long messages
            max_width = 560 + self.control_panel_width - 20
            text_surface = log_font.render(log_entry[:200], True, color)
            self.display.blit(text_surface, (10, y))
            y += line_height
            
            if y >= log_panel_y + self.log_panel_height - 10:
                break
    
    def _calculate_divided_voltage(self):
        """Calculate the voltage after resistor divider (what ADC actually sees)"""
        # Voltage divider formula: Vout = Vin * R2 / (R1 + R2)
        battery_voltage_mV = self.adc_voltage * 1000  # Convert V to mV
        divided_voltage_mV = battery_voltage_mV * self.resistor_r2 / (self.resistor_r1 + self.resistor_r2)
        return divided_voltage_mV
    
    def _apply_shake(self):
        """Apply shake effect to accelerometer"""
        # Generate random acceleration values with specified magnitude
        self.accel_data = [
            random.uniform(-self.shake_magnitude, self.shake_magnitude),
            random.uniform(-self.shake_magnitude, self.shake_magnitude),
            random.uniform(-self.shake_magnitude, self.shake_magnitude)
        ]
        log_msg = f'Shake applied: X={self.accel_data[0]:.2f}g Y={self.accel_data[1]:.2f}g Z={self.accel_data[2]:.2f}g'
        if self.logger:
            self.logger.log_info(log_msg)
        self.add_log_message(log_msg, 'INFO')
        
        # Queue motion interrupt on pin 34 (LIS3DH INT2 pin)
        self.interrupt_queue.append({'pin': 34, 'edge': 'rising'})
        if self.logger:
            self.logger.log_info('Motion interrupt queued for pin 34')
        self.add_log_message('Motion interrupt queued for pin 34', 'INFO')
    
    def _decay_shake(self):
        """Gradually return accelerometer to rest state (0, 0, 1g)"""
        decay_rate = 0.1
        self.accel_data[0] *= (1 - decay_rate)
        self.accel_data[1] *= (1 - decay_rate)
        self.accel_data[2] = self.accel_data[2] * (1 - decay_rate) + 1.0 * decay_rate
    
    def rgb565_to_rgb(self, color):
        r = (color & 0xF800) >> 8
        g = (color & 0x07E0) >> 3
        b = (color & 0x001F) << 3
        return (r, g, b)

    def handle_command(self, command):
        screens = [self.screen1, self.screen2]
        if command['module'] == 'screenshot':
            if command['command'] == 'take':
                params = command.get('parameters', {})
                filepath = params.get('filepath')
                include_controls = params.get('include_controls', False)
                return self.take_screenshot(filepath, include_controls)
        elif command['module'] == 'button':
            if command['command'] == 'press':
                button = command['parameters'].get('button', 0)
                duration = command['parameters'].get('duration', 0.1)
                return self.simulate_button_press(button, duration)
        elif command['module'] == 'gc9a01':
            if command['command'] == 'fill':
                screens[command['parameters']['display']-1].fill(self.rgb565_to_rgb(command['parameters']['color']))
            elif command['command'] == 'pixel':
                screens[command['parameters']['display']-1].set_at(
                    (command['parameters']['x'], command['parameters']['y']),
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
                    (command['parameters']['x0'], command['parameters']['y0']),
                    (command['parameters']['x1'], command['parameters']['y1'])
                )
            elif command['command'] == 'write':
                if command['parameters']['font'] == 'fonts.arial32px':
                    font = pygame.font.Font('arial.ttf', 32)
                elif command['parameters']['font'] == 'fonts.arial16px':
                    font = pygame.font.Font('arial.ttf', 16)

                text_surface = font.render(
                    command['parameters']['string'],
                    True,
                    self.rgb565_to_rgb(command['parameters']['fg_color']),
                    self.rgb565_to_rgb(command['parameters']['bg_color'])
                )
                screens[command['parameters']['display']-1].blit(
                    text_surface,
                    (command['parameters']['x'], command['parameters']['y'])
                )
            elif command['command'] == 'text':
                try:
                    text_image = get_vga_text(command['parameters']['font'], command['parameters']['string'])
                    raw_str = text_image.tobytes("raw", 'RGBA')
                    text = pygame.image.fromstring(raw_str, text_image.size, 'RGBA')
                    screens[command['parameters']['display']-1].blit(
                        text,
                        (command['parameters']['x'], command['parameters']['y'])
                    )
                except Exception as e:
                    if self.logger:
                        self.logger.log_error(f'Error rendering text: {e}')
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
                    (command['parameters']['x'], command['parameters']['y'])
                )
            elif command['command'] == 'blit_buffer':
                # Handle framebuffer blit - buffer is in RGB565 format
                params = command['parameters']
                buffer_data = bytes(params['buffer'])
                width = params['width']
                height = params['height']
                x = params['x']
                y = params['y']
                
                # Convert RGB565 buffer to RGB888 for pygame
                pixels = []
                for i in range(0, len(buffer_data), 2):
                    rgb565 = buffer_data[i] | (buffer_data[i+1] << 8)
                    rgb888 = self.rgb565_to_rgb(rgb565)
                    pixels.extend(rgb888)
                
                if len(pixels) == width * height * 3:
                    try:
                        img_surface = pygame.image.frombuffer(
                            bytes(pixels), 
                            (width, height), 
                            'RGB'
                        )
                        screens[params['display']-1].blit(img_surface, (x, y))
                    except Exception as e:
                        if self.logger:
                            self.logger.log_error(f'Failed to blit buffer: {e}')
        elif command['module'] == 'pca9535':
            if command['command'] == 'get_inputs':
                return self.get_inputs(self.button_states)
        elif command['module'] == 'pin':
            if command['command'] == 'value':
                pin_num = command['parameters']['pin']
                if pin_num == 0:
                    return 0 if self.button_states[0] > 0 else 1
                return 1
            elif command['command'] == 'poll_interrupts':
                # Return and clear all pending interrupts
                interrupts = self.interrupt_queue.copy()
                self.interrupt_queue.clear()
                if interrupts and self.logger:
                    self.logger.log_info(f'Returning {len(interrupts)} pending interrupt(s)')
                return interrupts
        elif command['module'] == 'neopixel':
            if command['command'] == 'write':
                leds_grb = command['parameters']['leds'][:7]
                self.leds = [(r, b, g) for g, r, b in leds_grb]
        elif command['module'] == 'lis3dh':
            # Mock accelerometer data
            if command['command'] == 'acceleration' or command['command'] == 'get_acceleration':
                # Return current accel data
                return {
                    'x': self.accel_data[0],
                    'y': self.accel_data[1],
                    'z': self.accel_data[2]
                }
        elif command['module'] == 'adc':
            # Mock ADC readings (battery voltage, etc)
            if command['command'] == 'read' or command['command'] == 'get_voltage':
                divided_voltage = self._calculate_divided_voltage()
                return divided_voltage  # Return in mV

    def get_inputs(self, input_list):
        """Calculate PCA9535 input register value based on button states"""
        input_number = 0xFFFF
        
        for button_index in range(1, len(input_list)):
            button_time = input_list[button_index]
            if button_time > 0:
                iox_index = button_index - 1
                if iox_index < len(self.iox_button_map):
                    input_number &= ~self.iox_button_map[iox_index]
        
        return input_number

    def render_leds(self):
        """Render LED strip with glow effects"""
        if not self.show_leds:
            return
        
        led_x = 499
        led_y_start = 187
        led_y_delta = 108.7
        radius = 12
        led_positions = []
        for i in range(7):
            led_positions.append((led_x, led_y_start + i * led_y_delta))
        
        for i, (x, y) in enumerate(led_positions):
            if i < len(self.leds):
                r, g, b = self.leds[i]
                
                if r == 0 and g == 0 and b == 0:
                    pygame.draw.circle(self.display, (255, 255, 255), (x, y), radius, width=1)
                    continue
                
                glow_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (r//4, g//4, b//4, 80), (20, 20), 20)
                self.display.blit(glow_surface, (x-20, y-20), special_flags=pygame.BLEND_RGBA_ADD)
                
                glow_surface2 = pygame.Surface((24, 24), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface2, (r//2, g//2, b//2, 120), (12, 12), radius)
                self.display.blit(glow_surface2, (x-12, y-12), special_flags=pygame.BLEND_RGBA_ADD)
                
                pygame.draw.circle(self.display, (r, g, b), (x, y), radius)
                
                pygame.draw.circle(self.display, 
                                 (min(255, r+100), min(255, g+100), min(255, b+100)), 
                                 (x-2, y-2), 3)
    
    def render_button_click_areas(self):
        """Draw circles over button areas to show they're clickable"""
        for x, y, radius, button_idx in self.button_click_areas:
            # Draw semi-transparent overlay
            circle_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            
            # Check if button is currently pressed
            is_pressed = self.button_states[button_idx] > 0
            
            if is_pressed:
                # Highlight in green when pressed
                pygame.draw.circle(circle_surface, (0, 255, 0, 120), (radius, radius), radius)
            else:
                # Light blue outline when not pressed
                pygame.draw.circle(circle_surface, (100, 150, 255, 80), (radius, radius), radius)
                pygame.draw.circle(circle_surface, (100, 150, 255, 150), (radius, radius), radius, 2)
            
            self.display.blit(circle_surface, (x - radius, y - radius))
            
            # Draw button label
            label_font = pygame.font.Font(None, 20)
            label_text = f'{button_idx}'
            label_surface = label_font.render(label_text, True, (255, 255, 255))
            label_rect = label_surface.get_rect(center=(x, y))
            self.display.blit(label_surface, label_rect)
    
    def take_screenshot(self, filepath=None, include_controls=None):
        """Capture a screenshot of the simulator window
        
        Args:
            filepath: Optional custom path. If None, auto-generates filename.
            include_controls: Whether to include control panel. If None, uses checkbox state.
        
        Returns:
            Path to saved screenshot file
        """
        if filepath is None:
            # Auto-generate filename with timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = os.path.join(self.screenshot_dir, f'screenshot_{timestamp}_{self.screenshot_counter:04d}.png')
            self.screenshot_counter += 1
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
        
        # Use parameter if provided, otherwise use checkbox state
        if include_controls is None:
            include_controls = self.screenshot_include_controls
        
        # Determine what to capture
        if include_controls:
            # Save full display including control panel
            screenshot_surface = self.display
        else:
            # Crop to just the badge hardware (exclude control panel)
            badge_width = 560  # Width before control panel
            screenshot_surface = pygame.Surface((badge_width, self.display.get_height()))
            screenshot_surface.blit(self.display, (0, 0), area=pygame.Rect(0, 0, badge_width, self.display.get_height()))
        
        # Save the screenshot surface
        pygame.image.save(screenshot_surface, filepath)
        
        if self.logger:
            self.logger.log_info(f'Screenshot saved to: {filepath}')
        else:
            print(f'Screenshot saved to: {filepath}')
        
        # Return just the filepath - the JSON protocol handler will wrap it
        return filepath
    
    def simulate_button_press(self, button: int, duration: float = 0.1):
        """Simulate a button press programmatically
        
        Args:
            button: Button index (0-7)
            duration: How long to hold the button (seconds)
        
        Returns:
            Success status
        """
        import time
        import pygame
        
        if button < 0 or button >= len(self.button_states):
            return {'status': 'error', 'message': f'Invalid button index: {button}'}
        
        # Simulate button press by setting state
        press_time = pygame.time.get_ticks()
        self.button_states[button] = press_time
        
        if self.logger:
            self.logger.log_info(f'Button {button} pressed programmatically')
        
        # Note: The button will be released by the main event loop
        # after duration. For now, we'll just mark it as pressed.
        # The actual release timing is handled by the firmware polling.
        
        # Return just the result data - the JSON protocol handler will wrap it
        return {'button': button, 'duration': duration}
    
    def generate_circular_cutout(self, surface):
        circle_mask = pygame.Surface((240, 240), pygame.SRCALPHA)
        circle_mask.fill((0, 0, 0, 0))
        pygame.draw.circle(
            circle_mask, 
            (255, 255, 255, 255),
            (120, 120),
            120
        )

        circular_cutout = pygame.Surface((240, 240), pygame.SRCALPHA)
        circular_cutout.fill((0, 0, 0, 0))
        circular_cutout.blit(surface, (0, 0), area=pygame.Rect(0, 0, 240, 240))
        circular_cutout.blit(circle_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        return circular_cutout

    def gameloop(self):
        while self.running:
            time_delta = self.clock.tick(self.target_fps) / 1000.0
            current_time = pygame.time.get_ticks()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    # F12 for screenshot
                    if event.key == pygame.K_F12:
                        self.take_screenshot()
                    else:
                        button_idx = self.key_to_button.get(event.key)
                        if button_idx is not None and self.button_states[button_idx] == 0:
                            self.button_states[button_idx] = current_time
                            if self.logger:
                                self.logger.log_info(f'Button {button_idx} pressed (key {event.key})')
                            self.add_log_message(f'Button {button_idx} pressed (keyboard)', 'INFO')
                elif event.type == pygame.KEYUP:
                    button_idx = self.key_to_button.get(event.key)
                    if button_idx is not None and self.button_states[button_idx] > 0:
                        held_duration = current_time - self.button_states[button_idx]
                        self.button_states[button_idx] = 0
                        if self.logger:
                            self.logger.log_info(f'Button {button_idx} released after {held_duration}ms')
                        self.add_log_message(f'Button {button_idx} released after {held_duration}ms', 'INFO')
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if click is on a button area
                    if event.button == 1:  # Left click
                        mouse_x, mouse_y = event.pos
                        for bx, by, bradius, button_idx in self.button_click_areas:
                            # Calculate distance from click to button center
                            distance = ((mouse_x - bx) ** 2 + (mouse_y - by) ** 2) ** 0.5
                            if distance <= bradius and self.button_states[button_idx] == 0:
                                self.button_states[button_idx] = current_time
                                if self.logger:
                                    self.logger.log_info(f'Button {button_idx} pressed (mouse click)')
                                self.add_log_message(f'Button {button_idx} pressed (mouse click)', 'INFO')
                                break
                elif event.type == pygame.MOUSEBUTTONUP:
                    # Release any buttons that were clicked
                    if event.button == 1:  # Left click
                        mouse_x, mouse_y = event.pos
                        for bx, by, bradius, button_idx in self.button_click_areas:
                            distance = ((mouse_x - bx) ** 2 + (mouse_y - by) ** 2) ** 0.5
                            if distance <= bradius and self.button_states[button_idx] > 0:
                                held_duration = current_time - self.button_states[button_idx]
                                self.button_states[button_idx] = 0
                                if self.logger:
                                    self.logger.log_info(f'Button {button_idx} released after {held_duration}ms')
                                self.add_log_message(f'Button {button_idx} released after {held_duration}ms', 'INFO')
                                break
                elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.shake_button:
                        self._apply_shake()
                        self.add_log_message('Shake applied to accelerometer', 'INFO')
                    elif event.ui_element == self.screenshot_button:
                        self.take_screenshot()
                        self.add_log_message('Screenshot captured', 'INFO')
                    elif event.ui_element == self.screenshot_controls_checkbox:
                        # Toggle checkbox state
                        self.screenshot_include_controls = not self.screenshot_include_controls
                        checkbox_text = 'Screenshot Includes Controls' if self.screenshot_include_controls else 'Screenshot Excludes Controls'
                        self.screenshot_controls_checkbox.set_text(checkbox_text)
                        self.add_log_message(f'Screenshot mode: {"with" if self.screenshot_include_controls else "without"} controls', 'INFO')
                    elif event.ui_element == self.log_toggle_button:
                        # Toggle log panel
                        self.log_panel_collapsed = not self.log_panel_collapsed
                        if self.log_panel_collapsed:
                            self.log_toggle_button.set_text('Show Log Panel')
                            # Resize window to hide log panel
                            self.display = pygame.display.set_mode((560 + self.control_panel_width, 1060))
                            self.ui_manager.set_window_resolution((560 + self.control_panel_width, 1060))
                        else:
                            self.log_toggle_button.set_text('Hide Log Panel')
                            # Resize window to show log panel
                            self.display = pygame.display.set_mode((560 + self.control_panel_width, self.total_height))
                            self.ui_manager.set_window_resolution((560 + self.control_panel_width, self.total_height))
                        self.add_log_message(f'Log panel {"collapsed" if self.log_panel_collapsed else "expanded"}', 'INFO')
                elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    if event.ui_element == self.shake_slider:
                        self.shake_magnitude = event.value
                        self.shake_mag_label.set_text(f'Shake Magnitude: {self.shake_magnitude:.1f}g')
                    elif event.ui_element == self.adc_slider:
                        self.adc_voltage = event.value
                        self.adc_label.set_text(f'Battery Voltage: {self.adc_voltage:.2f}V')
                        self.divided_voltage_label.set_text(f'ADC sees: {self._calculate_divided_voltage():.0f}mV')
                    elif event.ui_element == self.r1_slider:
                        self.resistor_r1 = event.value
                        self.r1_label.set_text(f'R1 (top): {self.resistor_r1:.1f}kΩ')
                        self.divided_voltage_label.set_text(f'ADC sees: {self._calculate_divided_voltage():.0f}mV')
                    elif event.ui_element == self.r2_slider:
                        self.resistor_r2 = event.value
                        self.r2_label.set_text(f'R2 (bottom): {self.resistor_r2:.1f}kΩ')
                        self.divided_voltage_label.set_text(f'ADC sees: {self._calculate_divided_voltage():.0f}mV')
                elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if event.ui_element == self.charge_dropdown:
                        self.charge_state = event.text
                        if self.logger:
                            self.logger.log_info(f'Charge state changed to: {self.charge_state}')
                    elif event.ui_element == self.wifi_dropdown:
                        self.wifi_state = event.text
                        if self.logger:
                            self.logger.log_info(f'WiFi state changed to: {self.wifi_state}')
                    elif event.ui_element == self.bluetooth_dropdown:
                        self.bluetooth_state = event.text
                        if self.logger:
                            self.logger.log_info(f'Bluetooth state changed to: {self.bluetooth_state}')
                
                self.ui_manager.process_events(event)
            
            # Update accelerometer decay
            self._decay_shake()
            
            # Update accel display
            self.accel_display_label.set_text(
                f'X: {self.accel_data[0]:.2f}g Y: {self.accel_data[1]:.2f}g Z: {self.accel_data[2]:.2f}g'
            )
            
            # Update FPS display in control panel
            fps = self.clock.get_fps()
            self.fps_label.set_text(f'FPS: {fps:.1f}')
            
            # Update UI
            self.ui_manager.update(time_delta)
            
            # Render
            self.display.fill((30, 30, 30))  # Dark background
            self.display.blit(self.board_texture, (0, 0))
            self.render_leds()
            self.render_button_click_areas()  # Draw clickable button overlays
            self.display.blit(self.generate_circular_cutout(self.screen1), (70, 558))
            self.display.blit(self.generate_circular_cutout(self.screen2), (234, 774))
            
            # Draw log panel
            self.render_log_panel()
            
            # Draw UI
            self.ui_manager.draw_ui(self.display)
            
            pygame.display.update()
            self.frame_count += 1


# Binary Protocol Handler
# Command IDs (keep in sync with emulator_binary.py)
CMD_FILL = 0x01
CMD_PIXEL = 0x02
CMD_FILL_RECT = 0x03
CMD_LINE = 0x04
CMD_CIRCLE = 0x05
CMD_FILL_CIRCLE = 0x06
CMD_BLIT_BUFFER = 0x10
CMD_GET_INPUTS = 0x20
CMD_PIN_VALUE = 0x21
CMD_POLL_INTERRUPTS = 0x22
CMD_NEOPIXEL_WRITE = 0x30

class BinaryProtocolHandler:
    """Handles binary protocol commands for the GUI"""
    
    def __init__(self, gui_instance):
        self.gui = gui_instance
        self.screens = [self.gui.screen1, self.gui.screen2]
    
    def rgb565_to_rgb(self, color):
        """Convert RGB565 to RGB888"""
        r = (color & 0xF800) >> 8
        g = (color & 0x07E0) >> 3
        b = (color & 0x001F) << 3
        return (r, g, b)
    
    def handle_command(self, cmd_id, payload):
        """Process binary command and return response (status, data)"""
        try:
            if cmd_id == CMD_FILL:
                return self._handle_fill(payload)
            elif cmd_id == CMD_PIXEL:
                return self._handle_pixel(payload)
            elif cmd_id == CMD_FILL_RECT:
                return self._handle_fill_rect(payload)
            elif cmd_id == CMD_LINE:
                return self._handle_line(payload)
            elif cmd_id == CMD_CIRCLE:
                return self._handle_circle(payload, filled=False)
            elif cmd_id == CMD_FILL_CIRCLE:
                return self._handle_circle(payload, filled=True)
            elif cmd_id == CMD_BLIT_BUFFER:
                return self._handle_blit_buffer(payload)
            elif cmd_id == CMD_GET_INPUTS:
                return self._handle_get_inputs()
            elif cmd_id == CMD_PIN_VALUE:
                return self._handle_pin_value(payload)
            elif cmd_id == CMD_POLL_INTERRUPTS:
                return self._handle_poll_interrupts()
            elif cmd_id == CMD_NEOPIXEL_WRITE:
                return self._handle_neopixel_write(payload)
            else:
                return (1, None)  # Unknown command
        except Exception as e:
            if self.gui.logger:
                self.gui.logger.log_error(f'Binary command error: {e}')
            return (1, None)
    
    def _handle_fill(self, payload):
        """Fill display with color"""
        import struct
        display, color = struct.unpack('<BH', payload)
        self.screens[display - 1].fill(self.rgb565_to_rgb(color))
        return (0, None)
    
    def _handle_pixel(self, payload):
        """Set individual pixel"""
        import struct
        display, x, y, color = struct.unpack('<BhhH', payload)
        self.screens[display - 1].set_at((x, y), self.rgb565_to_rgb(color))
        return (0, None)
    
    def _handle_fill_rect(self, payload):
        """Fill rectangle"""
        import struct
        display, x, y, w, h, color = struct.unpack('<BhhhhH', payload)
        pygame.draw.rect(
            self.screens[display - 1],
            self.rgb565_to_rgb(color),
            pygame.Rect(x, y, w, h)
        )
        return (0, None)
    
    def _handle_line(self, payload):
        """Draw line"""
        import struct
        display, x0, y0, x1, y1, color = struct.unpack('<BhhhhH', payload)
        pygame.draw.line(
            self.screens[display - 1],
            self.rgb565_to_rgb(color),
            (x0, y0),
            (x1, y1)
        )
        return (0, None)
    
    def _handle_circle(self, payload, filled=False):
        """Draw circle (filled or outline)"""
        import struct
        display, x, y, r, color = struct.unpack('<BhhhH', payload)
        pygame.draw.circle(
            self.screens[display - 1],
            self.rgb565_to_rgb(color),
            (x, y),
            r,
            draw_top_left=True,
            width=0 if filled else 1
        )
        return (0, None)
    
    def _handle_blit_buffer(self, payload):
        """Blit RGB565 buffer to display - OPTIMIZED"""
        import struct
        # Parse header
        header_size = struct.calcsize('<BhhHH')
        display, x, y, width, height = struct.unpack('<BhhHH', payload[:header_size])
        buffer_data = payload[header_size:]
        
        # Expected buffer size
        expected_size = width * height * 2  # RGB565 = 2 bytes per pixel
        if len(buffer_data) != expected_size:
            if self.gui.logger:
                self.gui.logger.log_error(
                    f'Buffer size mismatch: got {len(buffer_data)}, expected {expected_size}'
                )
            return (1, None)
        
        # Convert RGB565 buffer to RGB888 - optimized with list comprehension
        pixels = []
        for i in range(0, len(buffer_data), 2):
            rgb565 = buffer_data[i] | (buffer_data[i+1] << 8)
            rgb888 = self.rgb565_to_rgb(rgb565)
            pixels.extend(rgb888)
        
        # Create surface and blit
        try:
            img_surface = pygame.image.frombuffer(
                bytes(pixels),
                (width, height),
                'RGB'
            )
            self.screens[display - 1].blit(img_surface, (x, y))
        except Exception as e:
            if self.gui.logger:
                self.gui.logger.log_error(f'Failed to blit buffer: {e}')
            return (1, None)
        
        return (0, None)
    
    def _handle_get_inputs(self):
        """Get button input state"""
        import struct
        inputs = self.gui.get_inputs(self.gui.button_states)
        return (0, struct.pack('<H', inputs))
    
    def _handle_pin_value(self, payload):
        """Read GPIO pin value"""
        import struct
        pin_num = struct.unpack('<B', payload)[0]
        value = 1
        return (0, struct.pack('<B', value))
    
    def _handle_poll_interrupts(self):
        """Poll for pending interrupts"""
        import json
        interrupts = self.gui.interrupt_queue.copy()
        self.gui.interrupt_queue.clear()
        if interrupts and self.gui.logger:
            self.gui.logger.log_info(f'Returning {len(interrupts)} pending interrupt(s)')
        # Return as JSON encoded bytes
        return (0, json.dumps(interrupts).encode('utf-8'))
    
    def _handle_neopixel_write(self, payload):
        """Handle neopixel LED writes"""
        import struct
        # Payload is 7 LEDs * 3 bytes (GRB) = 21 bytes
        leds_grb = []
        for i in range(0, min(len(payload), 21), 3):
            if i + 2 < len(payload):
                g, r, b = struct.unpack('BBB', payload[i:i+3])
                leds_grb.append((g, r, b))
        # Convert from GRB to RGB for rendering
        self.gui.leds = [(r, b, g) for g, r, b in leds_grb]
        return (0, None)


if __name__ == '__main__':
    """Standalone GUI mode - connects to MicroPython backend via sockets"""
    import argparse
    import socket
    import json
    import select
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='Badge Simulator GUI (Standalone Mode)')
    parser.add_argument('--port', type=int, default=4455, help='JSON protocol port')
    parser.add_argument('--binary-port', type=int, default=4456, help='Binary protocol port')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    # Load config
    config = {}
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print('No config.json found, using defaults')
    
    # Create logger if available
    logger = None
    try:
        from logger import create_logger
        logger = create_logger(config)
    except ImportError:
        pass
    
    # Create GUI
    print('Starting GUI...')
    gui_instance = GUIEnhanced(config, logger)
    binary_handler = BinaryProtocolHandler(gui_instance)
    
    # Connect to backend sockets
    json_port = args.port
    binary_port = args.binary_port
    
    json_sock = None
    binary_sock = None
    
    print(f'Connecting to MicroPython backend on ports {json_port}/{binary_port}...')
    
    # Try to connect with retries
    import time
    for attempt in range(10):
        try:
            # Connect to JSON socket
            if json_sock is None:
                json_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                json_sock.connect(('localhost', json_port))
                json_sock.setblocking(False)
                print(f'✓ Connected to JSON protocol on port {json_port}')
            
            # Connect to binary socket  
            if binary_sock is None:
                binary_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                binary_sock.connect(('localhost', binary_port))
                binary_sock.setblocking(False)
                print(f'✓ Connected to binary protocol on port {binary_port}')
            
            break
        except (ConnectionRefusedError, OSError) as e:
            if attempt < 9:
                print(f'Connection attempt {attempt + 1}/10 failed, retrying...')
                time.sleep(0.5)
            else:
                print(f'✗ Failed to connect to backend after 10 attempts')
                print(f'  Make sure MicroPython container is running')
                exit(1)
    
    print('✓ GUI connected to backend')
    print('Starting main loop...')
    
    # Main event loop
    clock = pygame.time.Clock()
    
    try:
        while gui_instance.running:
            time_delta = clock.tick(60) / 1000.0
            current_time = pygame.time.get_ticks()
            
            # Handle pygame events (copied from gameloop method)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gui_instance.running = False
                elif event.type == pygame.KEYDOWN:
                    # F12 for screenshot
                    if event.key == pygame.K_F12:
                        gui_instance.take_screenshot()
                    else:
                        button_idx = gui_instance.key_to_button.get(event.key)
                        if button_idx is not None and gui_instance.button_states[button_idx] == 0:
                            gui_instance.button_states[button_idx] = current_time
                            if logger:
                                logger.log_info(f'Button {button_idx} pressed (key {event.key})')
                            gui_instance.add_log_message(f'Button {button_idx} pressed (keyboard)', 'INFO')
                elif event.type == pygame.KEYUP:
                    button_idx = gui_instance.key_to_button.get(event.key)
                    if button_idx is not None and gui_instance.button_states[button_idx] > 0:
                        held_duration = current_time - gui_instance.button_states[button_idx]
                        gui_instance.button_states[button_idx] = 0
                        if logger:
                            logger.log_info(f'Button {button_idx} released after {held_duration}ms')
                        gui_instance.add_log_message(f'Button {button_idx} released after {held_duration}ms', 'INFO')
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_x, mouse_y = event.pos
                        for bx, by, bradius, button_idx in gui_instance.button_click_areas:
                            distance = ((mouse_x - bx) ** 2 + (mouse_y - by) ** 2) ** 0.5
                            if distance <= bradius and gui_instance.button_states[button_idx] == 0:
                                gui_instance.button_states[button_idx] = current_time
                                if logger:
                                    logger.log_info(f'Button {button_idx} pressed (mouse click)')
                                gui_instance.add_log_message(f'Button {button_idx} pressed (mouse click)', 'INFO')
                                break
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        mouse_x, mouse_y = event.pos
                        for bx, by, bradius, button_idx in gui_instance.button_click_areas:
                            distance = ((mouse_x - bx) ** 2 + (mouse_y - by) ** 2) ** 0.5
                            if distance <= bradius and gui_instance.button_states[button_idx] > 0:
                                held_duration = current_time - gui_instance.button_states[button_idx]
                                gui_instance.button_states[button_idx] = 0
                                if logger:
                                    logger.log_info(f'Button {button_idx} released after {held_duration}ms')
                                gui_instance.add_log_message(f'Button {button_idx} released after {held_duration}ms', 'INFO')
                                break
                
                # Let UI manager handle its events
                gui_instance.ui_manager.process_events(event)
            
            # Check for socket data
            readable, _, _ = select.select([json_sock, binary_sock], [], [], 0)
            
            for sock in readable:
                try:
                    if sock == binary_sock:
                        # Handle binary protocol messages
                        data = sock.recv(8192)
                        if data:
                            binary_handler.handle_data(data)
                    elif sock == json_sock:
                        # Handle JSON protocol messages
                        data = sock.recv(8192)
                        if data:
                            # Process JSON commands if needed
                            pass
                except Exception as e:
                    if args.verbose:
                        print(f'Socket error: {e}')
            
            # Update GUI
            gui_instance.ui_manager.update(time_delta)
            
            # Render (copied from gameloop)
            gui_instance.display.fill((30, 30, 30))
            gui_instance.display.blit(gui_instance.board_texture, (0, 0))
            
            # Render screens
            gui_instance.display.blit(gui_instance.screen1, (160, 180))
            gui_instance.display.blit(gui_instance.screen2, (160, 640))
            
            # Render LEDs if enabled
            if gui_instance.show_leds:
                gui_instance.render_leds()
            
            # Render button click areas if enabled
            if gui_instance.config.get('gui', {}).get('show_button_areas', False):
                gui_instance.render_button_click_areas()
            
            # Draw UI
            gui_instance.ui_manager.draw_ui(gui_instance.display)
            
            # Render log panel if expanded
            if not gui_instance.log_panel_collapsed:
                gui_instance.render_log_panel()
            
            # Show FPS if enabled
            if gui_instance.show_fps:
                gui_instance.frame_count += 1
                fps = gui_instance.clock.get_fps()
                fps_text = gui_instance.fps_display_font.render(f'FPS: {fps:.1f}', True, (255, 255, 255))
                gui_instance.display.blit(fps_text, (10, 10))
            
            pygame.display.flip()

            
    except KeyboardInterrupt:
        print('\nShutting down GUI...')
    finally:
        if json_sock:
            json_sock.close()
        if binary_sock:
            binary_sock.close()
        pygame.quit()
        print('GUI shutdown complete')
