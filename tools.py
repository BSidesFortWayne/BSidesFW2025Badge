from typer import Typer
import os

app = Typer()

@app.command()
def deploy_all_to_device(files: list[str] = []):
    # Use mpremote to sync src/ folder to the device root
    # Execute this shell command
    # mpremote cp src/* :

    print("Syncing files to device")
    print(files)

    os.system("mpremote cp src/* :")


if __name__ == "__main__":
    app()
