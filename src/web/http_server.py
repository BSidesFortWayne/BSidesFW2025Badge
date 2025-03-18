import socket
import asyncio

html = """<!DOCTYPE html>
<html>
    <head>
        <title>Hello World Title</title>
    </head>
    <body>
        <h1>Hello World H1</h1>
    </body>
</html>
"""

class HTTPServer:
    port: int
    addr: str
    running: bool
    s: socket.socket

    def __init__(self, addr='0.0.0.0', port=80):
        self.addr = addr
        self.port = port
        self.s = socket.socket()
        self.running = False

    def start(self):
        self.running = True
        asyncio.create_task(self.run())

    def stop(self):
        self.running = False

    async def run(self):
        self.s.bind(socket.getaddrinfo(self.addr, self.port)[0][-1])
        self.s.listen(1)
        print('listening on', self.addr)
        while self.running:
            cl, addr = self.s.accept()
            print('client connected from', addr)
            cl_file = cl.makefile('rwb', 0)
            while True:
                line = cl_file.readline()
                if not line or line == b'\r\n':
                    break
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n') # type: ignore TODO why doesn't this type work?
            cl.send(html) # type: ignore TODO why doesn't this type work?
            cl.close()
        
        self.s.close()

    