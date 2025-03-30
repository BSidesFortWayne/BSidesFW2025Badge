import time
import gc

from controller import Controller
from lib.http_server import start_http_server

gc.enable()
gc.collect()


async def main():
    controller = Controller()

    # TODO conditionally start based on 
    # - Network is started
    # - User has setup configuration to auto-run HTTP server
    asyncio.create_task(start_http_server(controller))

    total_times = 0
    total_counts = 0
    while True:
        x = time.ticks_ms()
        current_view = controller.current_view
        if current_view:
            await current_view.update()
        await asyncio.sleep(0.01)
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