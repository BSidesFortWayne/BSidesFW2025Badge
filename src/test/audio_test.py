import asyncio
from bsp import BSP
from hardware_rev import HardwareRev


bsp = BSP(HardwareRev.V2)

bsp.speaker.start_tetris()


async def test_speaker():
    while True:
        await asyncio.sleep(1)
        print("Playing")


asyncio.create_task(test_speaker())