import asyncio
import network

from controller import Controller
from lib.dns import MicroDNSSrv
from lib.microdot.microdot import Microdot, Response


async def start_wifi(mode: str, ssid: str, password: str):
    # TODO load config from file

    if mode == "STA":
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        sta_if.connect(ssid, password)
    elif mode == "AP":
        sta_if = network.WLAN(network.AP_IF)
        sta_if.active(True)
        sta_if.config(essid=ssid, password=password)

    while not sta_if.active():
        await asyncio.sleep(0.01)
    
    MicroDNSSrv.Create({ '*' : sta_if.ifconfig()[0] })

    print(sta_if.ifconfig())


async def start_http_server(controller: Controller):
    print("Starting HTTP Server")
    import json
    app = Microdot()
    app.debug = True

    Response.default_content_type = 'text/html'

    @app.route('/config', methods=['GET', 'POST'])
    async def index(request):
        if not controller.current_view:
            Microdot.abort(404)
            # This doesn't actually return anything, we're just returning to make the linter happy
            return
        
        if request.method == 'POST':
            # TODO validate the value
            try:
                controller.current_view.config.update(json.loads(request.body))
            except Exception as ex:
                print(ex)
                Microdot.abort(500)
        return json.dumps(controller.current_view.config)
    

    @app.route('/config/<key>', methods=['GET', 'POST'])
    async def get_key(request, key):
        if not controller.current_view:
            Microdot.abort(404)
            # This doesn't actually return anything, we're just returning to make the linter happy
            return
        
        if request.method == 'POST':
            try:
                controller.current_view.config[key] = json.loads(request.body)
            except Exception as ex:
                print(ex)
                Microdot.abort(500)
        return json.dumps(controller.current_view.config)
    
    app.run(port=80)
