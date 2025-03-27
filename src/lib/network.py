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
        print(f"Connecting to {ssid} with password {password}")
        sta_if.connect(ssid, password)
        while not sta_if.isconnected():
            await asyncio.sleep(0.01)
    elif mode == "AP":
        sta_if = network.WLAN(network.AP_IF)
        sta_if.active(True)
        sta_if.config(essid=ssid, password=password)
        while not sta_if.active():
            await asyncio.sleep(0.01)

    MicroDNSSrv.Create({"*": sta_if.ifconfig()[0]})

    print(sta_if.ifconfig())


async def start_http_server(controller: Controller):
    print("Starting HTTP Server")
    import json

    app = Microdot()
    app.debug = True

    Response.default_content_type = "text/html"

    @app.route("/_config", methods=["GET", "POST"])
    async def config_json(request: Request):
        if not controller.current_view:
            Microdot.abort(404)
            # This doesn't actually return anything, we're just returning to make the linter happy
            return

        config = controller.current_view.config
        if request.method == "POST":
            # TODO validate the value
            try:
                print(request.body)
                print(request.json)
                config.update(request.json) # type: ignore
                # redirect back to /config for web users
                Response.redirect("/config")
            except Exception as ex:
                print(ex)
                Microdot.abort(500)
        return json.dumps(controller.current_view.config)

    # TODO do we need this endpoint? Maybe not?
    @app.route("/_config/<key>", methods=["GET", "POST"])
    async def get_key(request: Request, key: str):
        if not controller.current_view:
            Microdot.abort(404)
            # This doesn't actually return anything, we're just returning to make the linter happy
            return

        if request.method == "POST":
            try:
                config = controller.current_view.config
                config.update({key: request.json}) 
            except Exception as ex:
                print(ex)
                Microdot.abort(500)
        return json.dumps(controller.current_view.config)

    @app.route("/config")
    async def config_web(request: Request):
        if not controller.current_view:
            Microdot.abort(404)
            # This doesn't actually return anything, we're just returning to make the linter happy
            return

        config = controller.current_view.config
        title = f"{controller.current_view.name} Config"
        # Return basic html
        return f"""
        <html>
            <head>
                <title>{title}</title>
                <style>
                    form label, form input {{
                        display: block;
                        margin-bottom: 10px;
                    }}
                </style>
                <script>
                    function updateCheckboxValue(checkbox) {{
                        // Update the value attribute based on the checked state
                        checkbox.value = checkbox.checked ? "true" : "false";
                    }}
                    // an alternative to this would be the parse the form data on the microcontroller instead
                    function myFunction(form) {{
                        const formData = new FormData(form);
                        console.log(formData);
                        var object = {{}};
                        formData.forEach((value, key) => object[key] = value);
                        var json = JSON.stringify(object);
                        
                        // Send the JSON to the server
                        fetch('/_config', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json'
                            }},
                            body: json
                        }})
                        .then(response => {{
                            if (response.ok) {{
                                // draw on an element with text that shows the update time
                                var status = document.getElementById("status");
                                status.innerText = "Config updated at " + new Date().toLocaleTimeString();
                            }} else {{
                                var status = document.getElementById("status");
                                status.innerText = "Error updating config";
                            }}
                        }})
                        .catch(error => {{
                            console.error("Error submitting config:", error);
                            alert("An error occurred.");
                        }});
                    }}
                </script>
            </head>
            <body>
                <h1>{title}</h1>
                <form onsubmit="event.preventDefault(); myFunction(this);">
                    {config.as_html()}
                    <input type="submit" value="Submit">
                </form>
                <div id="status"></div>
            </body>
        </html>
        """

    app.run(port=80)
