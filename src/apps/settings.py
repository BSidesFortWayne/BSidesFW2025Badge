from apps.app import BaseApp
import gc9a01 
from time import sleep_ms

import fonts.arial32px as arial32px
from lib.random_password import generate_random_password
from lib.uQR import QRCode, QRData, MODE_8BIT_BYTE
from lib.dns import MicroDNSSrv
from lib.microdot import Microdot, Response
import asyncio


class App(BaseApp):
    def __init__(self, controller):
        super().__init__(controller, "Settings")
        self.display1 = self.controller.bsp.displays.display1
        self.display2 = self.controller.bsp.displays.display2

        self.bg_color = gc9a01.WHITE
        self.fg_color = gc9a01.BLACK
        
        self.font = arial32px

        self.center = self.display1.width() // 2

        self.display1.fill(gc9a01.WHITE)
        self.display2.fill(gc9a01.WHITE)

        self.draw_status()

        # TODO start random password generation and QRCode generation
        # on a thread and mark loading until complete
        self.random_password = generate_random_password()
        self.ssid = f'Badge {generate_random_password()}'
        qr_data = QRData(f'WIFI:S:{self.ssid};T:WPA;P:{self.random_password};H:false;;'.encode(), mode=MODE_8BIT_BYTE)

        self.qr = QRCode()
        self.qr.add_data(qr_data) # WiFi QR code

        self.start_wifi(self.ssid, self.random_password)

        asyncio.create_task(self.start_website())

        print(f"Pre-fill, SSID is \"{self.ssid}\", password is {self.random_password}")

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

    def start_wifi(self, essid, password):
        import network

        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        ap.config(essid=essid, authmode=network.AUTH_WPA_WPA2_PSK, password=password)

        while not ap.active():
            sleep_ms(10)
        
        MicroDNSSrv.Create({ '*' : ap.ifconfig()[0] })
    
    async def start_website(self):
        app = Microdot()

        Response.default_content_type = 'text/html'

        @app.before_request
        def home(request):
            return '<h1>Hello, World!</h1>'
        
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
    