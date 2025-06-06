import time
import gc

from controller import Controller

gc.enable()
gc.collect()


async def main(displays):
    controller = Controller(displays)

    # Main thread, should be last to run
    asyncio.create_task(controller.run())

    while True:
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main(displays))
