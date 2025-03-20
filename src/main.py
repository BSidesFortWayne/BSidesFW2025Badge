import time
import gc

from controller import Controller


gc.enable()
gc.collect()


def test_http_server():
    import network

    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid="test123", password="abcd1234")

    while not ap.active():
        pass

    print('Connection successful')
    print(ap.ifconfig())

    from web.http_server import HTTPServer
    server = HTTPServer()
    server.start()

async def main():
    controller = Controller()

    total_times = 0
    total_counts = 0
    while True:
        x = time.ticks_ms()
        current_view = controller.current_view
        if current_view:
            current_view.update()
        await asyncio.sleep(0.05)
        d = time.ticks_diff(time.ticks_ms(), x)
        total_times += d
        total_counts += 1
        if total_counts % 100 == 0:
            average = total_times/total_counts
            print(f"Average: {average} ms")
            print(f"Average Hz: {int(1000/average)} Hz")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())