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




## Development: Getting Started

### Tools

The python packages in this repository are managed by `uv`. The repository structure is as follows

- `.venv`: This folder will be installed when you set up the python virtual environment with uv
- `.vscode`: Vscode specific settings for this project
- `schematics`: Board schematics as PDF
- `src`: The embedded code for deployment on the target
- `STLs`: Screen bezels, supports, and PCB STLs
- `typings`: Custom typings for the VSCode Python Language Server in order to get better typehints and support for the micropython code

### Setup

Install `uv` ([getting started](https://docs.astral.sh/uv/getting-started/installation/)) based on your OS of choice. If on Windows, you may have a better development experience in `WSL` if you can provide access to the ESP32 chip to the WSL instance ([Connect USB devices](https://learn.microsoft.com/en-us/windows/wsl/connect-usb)). However, `uv` and `mpremote` both work on Windows so you can also develop natively

### Using `mpremote` for on board development

Once you have `uv` setup, you can simply run

```shell
uv sync
```

to get the virtual environment set up. Once you plug in and turn on your dev board, you need to change the device permissions (Linux only)

```shell
sudo chmod a+x /dev/ttyUSB0
```

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
