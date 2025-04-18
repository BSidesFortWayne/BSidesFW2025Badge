import typer
import os
import time
import mido
import json

import watchdog.events
from watchdog.observers import Observer

app = typer.Typer()

class FSEventHandler(watchdog.events.FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.last_modified = {}

    def file_change(self, event):
        if event.event_type == 'moved':
            os.system(f'mpremote cp {event.dest_path} {event.dest_path.replace('src', ':')}')
            os.system(f'mpremote rm {event.src_path.replace('src', ':')}')
        elif event.event_type == 'deleted':
            os.system(f'mpremote rm {event.src_path.replace('src', ':')}')
        elif event.event_type == 'modified':
            os.system(f'mpremote cp {event.src_path} {event.src_path.replace('src', ':')}')

    def on_any_event(self, event: watchdog.events.FileSystemEvent) -> None:
        if type(event) == watchdog.events.FileModifiedEvent or type(event) == watchdog.events.FileMovedEvent or type(event) == watchdog.events.FileDeletedEvent:
            now = time.time()
            last_time = self.last_modified.get(event.src_path, 0)
            if now - last_time > 3: # debounce
                self.file_change(event)
                self.last_modified[event.src_path] = now

@app.command()
def erase_flash(device="/dev/ttyUSB0"):
    """
    Erase the flash memory of the ESP32 device using esptool.
    """
    os.system("esptool.py --chip esp32 erase_flash")

@app.command()
def sync_on_change():
    """
    Listens for changes to the code, and automatically sends the changes to the board connected.
    """

    event_handler = FSEventHandler()
    observer = Observer()
    observer.schedule(event_handler, "src", recursive=True)
    observer.start()
    print('Listening for changes')
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()


@app.command()
def add_song(midi_filename: str, song_id: str):
    """
    Adds a MIDI file into the project that can be accessible in the code by the provided song id.
    """

    if not os.path.exists(midi_filename):
        raise typer.BadParameter('MIDI file does not exist.')
    
    if os.path.exists(f'src/songs/{song_id}.json'):
        raise typer.BadParameter('Song ID already in use.')
    
    mid = mido.MidiFile(midi_filename)
    
    notes_data = []
    time = 0
    tempo = 500000
    ticks_per_beat = mid.ticks_per_beat
    active_notes = {}
    
    for track in mid.tracks:
        for msg in track:
            time += msg.time
            
            if msg.type == 'set_tempo':
                tempo = msg.tempo
            
            if msg.type == 'note_on':
                frequency = 440 * 2 ** ((msg.note - 69) / 12)
                
                active_notes[msg.note] = {
                    'frequency': frequency,
                    'start_time': time
                }
            
            elif msg.type == 'note_off':
                if msg.note in active_notes:
                    note_data = active_notes.pop(msg.note)
                    start_time = note_data['start_time']
                    
                    duration_ticks = time - start_time
                    duration_seconds = (duration_ticks / ticks_per_beat) * (tempo / 1000000)
                    
                    notes_data.append((note_data['frequency'], duration_seconds))
    
    song_file = open(f'src/songs/{song_id}.json', 'x')
    song_file.write(json.dumps(notes_data))
    song_file.close()

@app.command()
def write_flash(
    file: str, 
    offset: int = 0x1000, 
    device: str = "/dev/ttyUSB0", 
    erase: bool = True,
    verbose: bool = False,
    baud_rate: int = 1843200,
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


@app.command(
    help="Write a .bin file to the flash"
)
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


@app.command(
    help="Automatically detect and program devices plugged into new USB ports"
)
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

@app.command(
    help="Offline generate an app cache based on the apps in a specific directory. Useful for debugging app directory issues"
)
def generate_app_cache(app_directory="src/apps"):
    from src.app_directory import AppDirectory
    app_dir = AppDirectory(app_directory)
    for module_name,module in app_dir.modules.items():
        print(module, module_name)
    

    
@app.command(
    help="Recursively copy `files` to the device root using mpremote. By default uses our src/ directory which is why this is called a 'deployment script'"
)
def deploy_app_to_device(files: list[str] = []):
    # Use mpremote to sync src/ folder to the device root
    # Execute this shell command
    # mpremote cp src/* :

    print("Syncing files to device")
    print(files)

    os.system("mpremote cp -r src/* :")

@app.command(
    help="Simple program to write name data to the badge. Sample for registration programming"
)
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
