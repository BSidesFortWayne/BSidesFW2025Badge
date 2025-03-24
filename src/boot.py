# boot.py -- run on boot-up
import machine
import asyncio
import json

from lib.network import start_wifi


frequency = 240_000_000

if machine.freq() != frequency:
    machine.freq(frequency)

try:
    with open('config/wifi.json') as f:
        wifi = json.load(f)
        # TODO also add auto start routine
        asyncio.create_task(start_wifi(
            wifi["mode"], 
            wifi["ssid"], 
            wifi["password"]
        ))
except Exception as ex:
    print(ex)
    print("No wifi config found")


