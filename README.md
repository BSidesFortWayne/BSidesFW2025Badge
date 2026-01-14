# BSidesFW2025Badge

## How to use your badge

Here are some basic instructions to get you started using your BSides 2025 Badge!

### Navigating the Menu

When your badge initially boots it will load the default badge application and show your name.
If you would like to explore other features of the badge, you can press and hold (long press) button D.

Button D is located at the top corner of the badge and can be long pressed while using any of the
applications to return to the main menu.

### Badge Button Descriptions

RST: Pressing RST will reset the badge.

A: Function button, varies by App.

B: Function button, varies by App.

C: Function button, varies by App.

D: Long press (hold) D to return to menu screen from any App.

SEL: SEL (Select) button is used in most Apps and the Menu for making a selection.

(Left): Used in Apps and Menu to navigate Left or Down.

(Right): Used in Apps and Menu to navigate Right or Up.

### Badge App Functionality

(Left): This button will cycle through available colors for the font.

(Right): This button will cycle through available colors for the background.

A: This button will change the lower display to have the BSides Fort Wayne 2025 logo.  
++++_note: using the (Left) or (Right) buttons will switch the display back to showing company name and status_++++

D: Long press (hold) D to return to the Main Menu

Settings will save between power cycles.

## Development: Getting Started

### Quick Setup

#### Simulator (No Hardware Needed - Fastest Start)

Perfect for badge app development without physical hardware.

```shell
cd simulator/
./run.sh    # That's it! Auto-detects everything
```

The script automatically:
- Detects and uses MicroPython if available (fastest)
- Offers to install MicroPython if not found
- Falls back to Docker mode if needed (easiest)
- Installs pygame if needed
- Always prompts before any installations

📖 **Full docs:** [simulator/README.md](simulator/README.md)

#### Hardware Development Setup

**1. Install uv (Python package manager):**
```shell
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.sh | iex"
```

**2. Install dependencies:**
```shell
uv sync
```

**3. For Linux hardware access:**
```shell
sudo chmod a+x /dev/ttyUSB0
```

See [PROGRAMMING.md](./PROGRAMMING.md) for `mpremote` usage and deployment.

#### VS Code Dev Container (Optional)

If you use VS Code:
1. Open this folder in VS Code
2. Click "Reopen in Container" when prompted
3. Everything is pre-configured! ✨

### Tools

The python packages in this repository are managed by `uv`. The repository structure is as follows

- `.devcontainer`: VS Code dev container configuration (optional)
- `.venv`: This folder will be installed when you set up the python virtual environment with uv
- `.vscode`: Vscode specific settings for this project
- `schematics`: Board schematics as PDF
- `simulator`: Badge simulator for off-hardware development
- `src`: The embedded code for deployment on the target
- `STLs`: Screen bezels, supports, and PCB STLs
- `typings`: Custom typings for the VSCode Python Language Server in order to get better typehints and support for the micropython code

### Using `mpremote` for on board development

Please see [The Programming Guide](./PROGRAMMING.md) for more details

### Hardware

Please see [The Hardware Specifications](./HARDWARE.md) for more details

### Off Board Unit Tests

`pytest` is used to run any hardware independent unit tests in the `tests/` folder with
the following command

```shell
uv run pytest tests
```

This runs the pytest command out of the `tests` folder.

TODO: Perhaps we can reference the src/ folder so that we can move the files in `src/test` to
`tests` to keep as functional tests? But they are different in that we will run the functional
onboard tests with `mpremote run src/test/<test_file.py>`

## Custom Base Image Instructions

```bash
# Move to BSFW Custom Firmware
cd BSidesFW2025Badge/firmware

# Sync uv with project
uv sync

# Erase current flash and write new flash binary
uv run esptool.py erase_flash
uv run esptool.py --baud 460800 write_flash 0x1000 BSFWCustom_firmware_SPIRAM_with_GC9A01.bin
```

Please see the [Firmware Writeup](./firmware/README.md) for more information.
