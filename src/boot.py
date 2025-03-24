# boot.py -- run on boot-up
import machine
import asyncio

from lib.network import start_wifi


frequency = 240_000_000

if machine.freq() != frequency:
    machine.freq(frequency)

asyncio.create_task(start_wifi("AP", "ubnt-spy-24ghz", "ubntnotforyouonlyforme"))
