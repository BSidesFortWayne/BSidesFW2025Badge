def run_app(constructor):
    from controller import Controller
    import asyncio

    controller = Controller()
    app = constructor(controller)
    while True:
        asyncio.run(app.update())