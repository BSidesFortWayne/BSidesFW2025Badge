import asyncio
import network

from controller import Controller
from lib.dns import MicroDNSSrv
from lib.microdot.microdot import Microdot, Request, Response


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

    @app.route('/_config', methods=['GET', 'POST'])
    async def config_json(request: Request):
        if not controller.current_view:
            Microdot.abort(404)
            # This doesn't actually return anything, we're just returning to make the linter happy
            return
        
        if request.method == 'POST':
            # TODO validate the value
            try:
                print(request.body)
                # b'last_second=0&radius=110&minuts_hand_color=65535&bg_color=65535&seconds_hand_color=10100&hours_hand_color=1000&fg_color=0&minutes_hand_color=65535&minute_hand_color=65535&redraw_method=2&numbers_color=0'
                print(request.form)
                # {'last_second': ['0'], 'radius': ['110'], 'minuts_hand_color': ['65535'], 'numbers_color': ['0'], 'seconds_hand_color': ['10100'], 'hours_hand_color': ['1000'], 'fg_color': ['0'], 'minutes_hand_color': ['65535'], 'minute_hand_color': ['65535'], 'redraw_method': ['2'], 'bg_color': ['65535']}
                print(request.json)
                controller.current_view.config.update(json.loads(request.body))
                # redirect back to /config for web users
                Response.redirect("/config")
            except Exception as ex:
                print(ex)
                Microdot.abort(500)
        return json.dumps(controller.current_view.config)
    

    @app.route('/_config/<key>', methods=['GET', 'POST'])
    async def get_key(request: Request, key):
        if not controller.current_view:
            Microdot.abort(404)
            # This doesn't actually return anything, we're just returning to make the linter happy
            return
        
        if request.method == 'POST':
            try:
                print(request.body)
                print(request.form)
                print(request.json)
                controller.current_view.config[key] = request.json
            except Exception as ex:
                print(ex)
                Microdot.abort(500)
        return json.dumps(controller.current_view.config)
    
    def config_item_to_html(key, value):
        return f"""
        <label for="{key}">{key}</label>
        <input type="text" name="{key}" value="{value}">
        """
    
    @app.route('/config')
    async def config_web(request: Request):
        if not controller.current_view:
            Microdot.abort(404)
            # This doesn't actually return anything, we're just returning to make the linter happy
            return
        
        config = controller.current_view.config
        # Return basic html
        return f"""
        <html>
            <head>
                <title>Config</title>
            </head>
            <body>
                <h1>Config</h1>
                <form action="/_config" method="POST">
                    {"".join([config_item_to_html(k, v) for k, v in config.items()])}
                    <input type="submit" value="Submit">
                </form>
            </body>
        </html>
        """
        

    app.run(port=80)
