import time
import gc

from controller import Controller
from web.http_server import start_http_server

gc.enable()
gc.collect()


async def main(displays):
    controller = Controller(displays)
    # TODO conditionally start based on 
    # - Network is started
    # - User has setup configuration to auto-run HTTP server
    asyncio.create_task(start_http_server(controller))

    # Main thread, should be last to run
    asyncio.create_task(controller.run())

    while True:
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main(displays))
