from typer import Typer
import os
import time

app = Typer()


@app.command()
def program_device(firmware: str = "firmware_SPIRAM_8MiB.bin", reinstall_base_image: bool = False):
    # TODO I wonder if we can import esptool.py and mpremote directly as their python modules
    # Pros: we would get autocomplete and intellisense for running those tools
    # Cons: using the system command line calls is very straightforward and internal usage of those
    # libraries could be more fragile
    if reinstall_base_image:
        # erase flash with esptool
        os.system("esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash")

        # flash firmware with esptool
        os.system(f"esptool.py --chip esp32 --baud 460800 --port /dev/ttyUSB0 write_flash -z 0x1000 {firmware}")
        
        # Add 2 second delay for reset
        time.sleep(2)

    # Load python code with mpremote
    os.system("mpremote cp -r src/* :")

@app.command()
def generate_app_cache(app_directory="src/apps"):
    from src.app_directory import AppDirectory
    app_dir = AppDirectory(app_directory)
    for module_name,module in app_dir.modules.items():
        print(module, module_name)
    

    
@app.command()
def deploy_all_to_device(files: list[str] = []):
    # Use mpremote to sync src/ folder to the device root
    # Execute this shell command
    # mpremote cp src/* :

    print("Syncing files to device")
    print(files)

    os.system("mpremote cp src/* :")


def program_name(
    first_name: str,
    last_name: str,
    company: str = "",
    title: str = "",
):
    # Write to temporary JSON file
    with open("name.json", "w") as f:
        f.write(
            f"""
                {{
                    "first_name": "{first_name}",
                    "last_name": "{last_name}",
                    "company": "{company}",
                    "title": "{title}"
                }}
                """
        )
    
    # Execute this shell command
    os.system("uv run mpremote cp name.json :")

if __name__ == "__main__":
    app()
