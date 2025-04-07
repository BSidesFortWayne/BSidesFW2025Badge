from typer import Typer
import os
import time

app = Typer()


@app.command()
def erase_flash(device="/dev/ttyUSB0"):
    """
    Erase the flash memory of the ESP32 device using esptool.
    """
    os.system("esptool.py --chip esp32 erase_flash")

@app.command()
def write_flash(
    file: str, 
    offset: int = 0x1000, 
    device: str = "/dev/ttyUSB0", 
    erase: bool = True,
    verbose: bool = False,
    baud_rate: int = 460800,
):
    """
    Write a file to the ESP32 device using mpremote.
    """
    start_time = time.time()
    if erase:
        # Erase the flash memory first
        # TODO if not verbose, suppress output or make silent?
        os.system(f"esptool.py --chip esp32 --port {device} erase_flash")
        time.sleep(2)

    # Execute this shell command
    # TODO if not verbose, suppress output or make silent?
    os.system(f"esptool.py --chip esp32 --baud {baud_rate} --port {device} write_flash -z {hex(offset)} {file}")
    end_time = time.time()
    elapsed_time = end_time - start_time
    if verbose:
        print(f"Flash write time: {elapsed_time:.2f} seconds")
    
    return elapsed_time


@app.command()
def program_device(
    firmware: str = "firmware_SPIRAM_8MiB.bin", 
    reinstall_base_image: bool = False,
    device: str = "/dev/ttyUSB0",
    verbose: bool = True,
):
    # TODO I wonder if we can import esptool.py and mpremote directly as their python modules
    # Pros: we would get autocomplete and intellisense for running those tools
    # Cons: using the system command line calls is very straightforward and internal usage of those
    # libraries could be more fragile
    if reinstall_base_image:
        # flash firmware with esptool
        flash_write_time = write_flash(firmware, device=device, erase=True, verbose=verbose)
        
        # Add 2 second delay for reset
        time.sleep(2)

    # Load python code with mpremote
    start_file_send_time = time.time()
    os.system("mpremote cp -r src/* :")
    end_file_send_time = time.time()
    elapsed_file_send_time = end_file_send_time - start_file_send_time
    if verbose:
        print(f"File send time: {elapsed_file_send_time:.2f} seconds")
    # Add 2 second delay for reset
    time.sleep(2)

    os.system('mpremote reset')


@app.command()
def auto_programmer():
    """
    Automatically program the device with the latest firmware and code.

    Look for new devices to be plugged in. Ideally if running on Linux should
    already have permissions set for all reasonable devices. Should spin off 
    programming scripts as separate asynchronous tasks that can be started and 
    stopped, and cancelled if hanging.
    - Master thread - cancels a task if hasn't responded soon enough. Also
      responsible for drawing CLI that shows device connections and progress
    - Device identifier thread

    """

@app.command()
def generate_app_cache(app_directory="src/apps"):
    from src.app_directory import AppDirectory
    app_dir = AppDirectory(app_directory)
    for module_name,module in app_dir.modules.items():
        print(module, module_name)
    

    
@app.command()
def deploy_app_to_device(files: list[str] = []):
    # Use mpremote to sync src/ folder to the device root
    # Execute this shell command
    # mpremote cp src/* :

    print("Syncing files to device")
    print(files)

    os.system("mpremote cp -r src/* :")


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
