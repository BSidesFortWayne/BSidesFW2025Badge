import asyncio
import network

from controller import Controller
from lib.dns import MicroDNSSrv
from lib.microdot.microdot import Microdot, Request, Response


async def start_wifi(mode: str, ssid: str, password: str):
    # TODO load config from file

    if mode.upper() == "STA":
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        print(f"Connecting to {ssid} with password {password}")
        sta_if.connect(ssid, password)
        while not sta_if.isconnected():
            await asyncio.sleep(0.01)
    elif mode.upper() == "AP":
        sta_if = network.WLAN(network.AP_IF)
        sta_if.active(True)
        sta_if.config(essid=ssid, password=password)
        while not sta_if.active():
            await asyncio.sleep(0.01)

    MicroDNSSrv.Create({"*": sta_if.ifconfig()[0]})

    print(sta_if.ifconfig())


