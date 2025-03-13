from typer import Typer

app = Typer()

@app.command()
def sync_to_device(files: list[str] = []):
    print("Syncing to device")
    