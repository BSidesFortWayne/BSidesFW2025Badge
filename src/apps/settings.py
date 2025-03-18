from apps.app import BaseApp
import gc9a01 
from time import sleep_ms

import fonts.arial32px as arial32px
from lib.random_password import generate_random_password
from lib.uQR import QRCode


class App(BaseApp):
    name = "QR Code"
    def __init__(self, controller):
        super().__init__(controller)
        self.display1 = self.controller.bsp.displays.display1

        self.bg_color = gc9a01.WHITE
        self.fg_color = gc9a01.BLACK
        
        self.font = arial32px

        self.center = self.display1.width() // 2

        # TODO start random password generation and QRCode generation
        # on a thread and mark loading until complete
        self.random_password = generate_random_password()

        self.qr = QRCode()
        self.qr.add_data(self.random_password)

    def draw_status(self, status: str = 'Loading...'):
        self.display1.fill(gc9a01.WHITE)
        self.display1.write(
            self.font,
            'Loading...',
            10,
            100,
            gc9a01.BLACK,
            gc9a01.WHITE
        )

    def update(self):
        print(f"Pre-fill, password is {self.random_password}")
        self.display1.fill(gc9a01.WHITE)

        if self.qr is None:
            self.draw_status()
            return
        
        matrix = self.qr.get_matrix()
        if matrix is None or matrix[0] is None:
            self.draw_status("Error Generating")
            return
        
        for y, row in enumerate(matrix):
            for x, value in enumerate(row): # type: ignore
                if value:
                    # TODO calculate width and height and scale?
                    self.display1.fill_rect(30+x*5, 30+y*5, 5, 5, gc9a01.BLACK)
    
        sleep_ms(1000)

    