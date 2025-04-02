from controller import Controller
from lib.microdot.microdot import Microdot, Request, Response


async def start_http_server(controller: Controller):
    print("Starting HTTP Server")
    import json

    app = Microdot()
    app.debug = True

    Response.default_content_type = "text/html"

    # This is effective a JSON API for the config, so we'll "hide" it at _config
    # This is used for the form served from /config to accept the update config/form 
    # value
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
                # TODO if we instead use `request.form` and then do the validation in code
                # we could deliver a slightly smaller payload...
                config.update(request.json) # type: ignore
                # redirect back to /config for web users...
                # Could also serve a simple config success page?
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


    @app.route("/apps")
    async def apps(request: Request):
        if not controller.current_view:
            Microdot.abort(404)
            # This doesn't actually return anything, we're just returning to make the linter happy
            return

        apps = sorted(controller.app_directory, key=lambda app: app.friendly_name)
        app_list_html = "".join(
            f'<li><a href="/apps/switch/{app.friendly_name}">{app.friendly_name}</a></li>'
            for app in apps
        )

        # Return basic html
        return f"""
        <html>
            <head>
                <title>Apps</title>
            </head>
            <body>
                <h1>Apps</h1>
                <ul>
                    {app_list_html}
                </ul>
            </body>
        </html>
        """

    @app.route("/apps/switch/<app_name>")
    async def switch_app(request: Request, app_name: str):
        if not controller.current_view:
            Microdot.abort(404)
            # This doesn't actually return anything, we're just returning to make the linter happy
            return

        # unescape the app name to get rid of HTML escape codes
        app_name = app_name.replace("%20", " ")
        controller.switch_app(app_name)
        Response.redirect("/apps")

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
