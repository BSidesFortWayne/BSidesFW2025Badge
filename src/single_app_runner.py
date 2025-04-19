import time
def run_app(constructor, perf: bool = False, perf_rate_s: int = 5):
    from controller import Controller
    import asyncio

    controller = Controller(load_menu=False)
    app = constructor(controller)
    last_loop_time_ns = time.time_ns()
    renders = 0
    while True:
        asyncio.run(app.update())
        renders += 1
        if perf:
            current_time_ns = time.time_ns()
            elapsed_time_s = (current_time_ns - last_loop_time_ns) / 1_000_000_000
            if elapsed_time_s >= perf_rate_s:
                print(f"FPS: {renders / elapsed_time_s:.2f}")
                last_loop_time_ns = current_time_ns
                renders = 0
            
