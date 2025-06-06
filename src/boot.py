# boot.py -- run on boot-up
import machine
import asyncio
import json
import drivers.displays

# Loading the displays first to show the boot screen
print('Showing boot screen..')
displays = drivers.displays.Displays()

frequency = 240_000_000

if machine.freq() != frequency:
    machine.freq(frequency)

