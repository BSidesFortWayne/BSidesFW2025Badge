from apps.app import BaseApp
import gc9a01 
from time import sleep_ms

import fonts.arial32px as arial32px
from lib.random_password import generate_random_password
from lib.uQR import QRCode, QRData, MODE_8BIT_BYTE
from lib.dns import MicroDNSSrv
from lib.microdot import Microdot, Response, send_file, with_form_data
from lib.microdot.utemplate import Template
import asyncio
import os
import json

from lib.smart_config import BoolDropdownConfig, ColorConfig, EnumConfig

def hex_to_rgb565(hex_color: str) -> int:
    hex_color = hex_color.lower().lstrip('#')
    if len(hex_color) != 6:
        raise ValueError("Input must be a 6-digit hex colour in RRGGBB format")

    # Split into 8-bit RGB components
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    # Pack into 5-6-5 bits: RRRR R GGGGGG BBBB B
    rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return rgb565

def rgb565_to_hex(rgb565: int) -> str:
    if not (0 <= rgb565 <= 0xFFFF):
        raise ValueError("Value must be in the range 0x0000–0xFFFF")

    # Extract 5-6-5 bit fields
    r5 = (rgb565 >> 11) & 0x1F       # 5 bits for red
    g6 = (rgb565 >> 5)  & 0x3F       # 6 bits for green
    b5 =  rgb565        & 0x1F       # 5 bits for blue

    # Expand to 8-bit channels:
    # 5-bit -> 8-bit: replicate the high 5 bits (<<3) and copy top 3 again (>>2)
    # 6-bit -> 8-bit: replicate the high 6 bits (<<2) and copy top 2 again (>>4)
    r8 = (r5 << 3) | (r5 >> 2)
    g8 = (g6 << 2) | (g6 >> 4)
    b8 = (b5 << 3) | (b5 >> 2)

    return f'#{r8:02X}{g8:02X}{b8:02X}'

class App(BaseApp):
    name = "Settings"
    def __init__(self, controller):
        super().__init__(controller)
        self.display1 = self.controller.bsp.displays.display1
        self.display2 = self.controller.bsp.displays.display2

        self.bg_color = gc9a01.WHITE
        self.fg_color = gc9a01.BLACK
        
        self.font = arial32px

        self.center = self.display1.width() // 2

        self.display1.fill(gc9a01.WHITE)
        self.display2.fill(gc9a01.WHITE)
        self.badge_id = generate_random_password()

        self.config['test_config_var'] = 'test'
        self.config.add('test_bool_config', BoolDropdownConfig('Test Bool Config', True))
        self.config.add('test_color_config', ColorConfig('Test Color Config', gc9a01.BLACK))
        self.config.add('test_enum_config', EnumConfig('Test Enum Config', ['Option 1', 'Option 2', 'Option 3'], 'Option 1'))

        self.draw_status()

        try: # no os.path.exists function
            wifi_file = open('wifi.json')
        except OSError:
            ap = True
        else:
            ap = False

        if not ap:
            wifi_file = open('wifi.json')
            wifi_config = json.loads(wifi_file.read())
            wifi_file.close()
            self.ssid = wifi_config['essid']
            self.password = wifi_config['password']

        # TODO start random password generation and QRCode generation
        # on a thread and mark loading until complete
        if ap:
            self.password = generate_random_password()
            self.ssid = f'Badge {self.badge_id}'
        qr_data = QRData(f'WIFI:S:{self.ssid};T:WPA;P:{self.password};H:false;;'.encode(), mode=MODE_8BIT_BYTE)

        self.qr = QRCode()
        self.qr.add_data(qr_data) # WiFi QR code

        self.start_wifi(self.ssid, self.password, ap=ap)

        asyncio.create_task(self.start_website())

        print(f"Pre-fill, SSID is \"{self.ssid}\", password is {self.password}")

        while self.qr is None:
            sleep_ms(10)
        
        matrix = self.qr.get_matrix()
        if matrix is None or matrix[0] is None:
            self.draw_status("Error Generating")
            return
        
        self.display1.fill(gc9a01.WHITE)

        for y, row in enumerate(matrix):
            for x, value in enumerate(row): # type: ignore
                if value:
                    # TODO calculate width and height and scale?
                    self.display1.fill_rect(15+x*5, 15+y*5, 5, 5, gc9a01.BLACK)

    def start_wifi(self, essid, password, ap=True):
        import network

        if ap:
            ap = network.WLAN(network.AP_IF)
            ap.active(True)
            ap.config(essid=essid, authmode=network.AUTH_WPA_WPA2_PSK, password=password)

            while not ap.active():
                sleep_ms(10)

            MicroDNSSrv.Create({ '*' : ap.ifconfig()[0] })
        
        else:
            sta_if = network.WLAN(network.STA_IF)
            sta_if.active(True)
            sta_if.connect(essid, password)

            while not sta_if.isconnected():
                sleep_ms(10)
        
            MicroDNSSrv.Create({ '*' : sta_if.ifconfig()[0] })

            print(sta_if.ifconfig())
    
    async def start_website(self):
        import json
        app = Microdot()
        app.debug = True

        Template.initialize('website/templates')

        Response.default_content_type = 'text/html'

        @app.route('/static/<path:path>')
        async def static(request, path):
            if '..' in path:
                # directory traversal
                return 'Not found', 404
            return send_file('/website/static/' + path, max_age=86400)

        @app.route('/')
        async def home(request):
            return Template('home.html').render(
                path='/',
                badge_id=self.badge_id,
                battery_voltage=str(self.controller.battery.mv_average.average()/100) + 'v',
                battery_percentage='{}%'.format(self.controller.battery.get_battery_percentage()),
                current_app=self.controller.current_view.name if self.controller.current_view else 'None',
            )



        @app.get('/add_app')
        async def add_app(request):
            # Get list of existing app files
            apps = [f[:-3] for f in os.listdir('apps') if f.endswith('.py') and f != '__init__.py']
            return Template('add_app.html').render(
                path='/add_app',
                apps=apps
            )

        @app.get('/get_app_code')
        async def get_app_code(request):
            app_name = request.args.get('app_name')
            if app_name:
                try:
                    with open(f'apps/{app_name}.py', 'r') as f:
                        return f.read()
                except:
                    return 'Error: App not found', 404
            return 'Error: No app specified', 400

        @app.post('/add_app/submit')
        @with_form_data
        async def handle_add_app(request):
            app_name = request.form['app_name']
            app_code = request.form['app_code']

            # Save the new app file
            with open(f'apps/{app_name}.py', 'w') as f:
                f.write(app_code)

        @app.get('/config')
        async def config(request):
            return Template('config.html').render(
                path='/config',
                rgb565_to_hex=rgb565_to_hex,
                app_configs=self.controller.app_configs.items()
            )
        
        
        @app.post('/config/update')
        @with_form_data
        async def update_config(request):
            print(request.form['appSelection'])
            app = request.form['appSelection']
            app_config = self.controller.app_configs[app]
            for config_name, value in request.form.items():
                if config_name not in app_config:
                    print(f"Skipping unknown config: {config_name} for app {app}")
                    continue
                existing_config = app_config[config_name]
                existing_type = type(existing_config)
                print(f"Updating {app} config: {config_name} = {value}")

                if existing_type is not str and existing_type is not int and 'type' in existing_config:
                    existing_config_type = existing_config['type']

                    # Convert value
                    if existing_config_type == 'BoolDropdownConfig':
                        # TODO weird hack for bools... fine for now, need to work it out better
                        # Don't ask :-) 
                        value = True if len(value) == 2 else False
                    else:
                        value = value[0]

                    
                    if existing_config_type == 'BoolDropdownConfig':
                        existing_config['current'] = value
                    if existing_config_type == 'EnumConfig':
                        existing_config['current'] = value
                    elif existing_config_type == 'ColorConfig':
                        existing_config['current'] = hex_to_rgb565(value)
                    elif existing_config_type == 'RangeConfig':
                        existing_config['current'] = int(value)
                elif existing_type is str:
                    self.controller.app_configs[app][config_name] = str(value[0])
                elif existing_type is int:
                    try:
                        self.controller.app_configs[app][config_name] = int(value[0])
                    except ValueError:
                        pass
                else:
                    print(f"Unknown config type for {app} {config_name}: {existing_type}")
                    

            # return Response.redirect('/config')
        app.run(port=80)

    def draw_status(self, status: str = 'Loading...'):
        self.display1.write(
            self.font,
            'Loading...',
            10,
            100,
            gc9a01.BLACK,
            gc9a01.WHITE
        )


if __name__ == "__main__":
    from single_app_runner import run_app
    run_app(App, perf=True)
