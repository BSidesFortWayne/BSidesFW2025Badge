# BSidesFW2025Badge

BSides Fort Wayne Badge Programming

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
# Get esp-idf
git clone -b v5.2.2 --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
git checkout v5.2.2
git submodule update --init --recursive

# Setup esp-idf
./install.sh esp32 # (or install.bat on Windows)
source export.sh   # (or export.bat on Windows)

# Clone micropython + gc9a01 repo for display support
git clone git@github.com:micropython/micropython.git
git clone https://github.com/russhughes/gc9a01_mpy.git

cd micropython/ports/esp32

make \
    BOARD=ESP32_GENERIC \
    BOARD_VARIANT=SPIRAM \
    USER_C_MODULES=../../../../gc9a01_mpy/src/micropython.cmake \
    FROZEN_MANIFEST=../../../../../../gc9a01_mpy/manifest.py \
    clean submodules all

make \
    BOARD=ESP32_GENERIC \
    BOARD_VARIANT=SPIRAM \
    USER_C_MODULES=../../../../gc9a01_mpy/src/micropython.cmake \
    FROZEN_MANIFEST=../../../../../../gc9a01_mpy/manifest.py \   
    erase deploy


make \
    BOARD=ESP32_GENERIC \
    USER_C_MODULES=../../../../gc9a01_mpy/src/micropython.cmake \
    FROZEN_MANIFEST=../../../../../../gc9a01_mpy/manifest.py \
    clean submodules all

make \
    BOARD=ESP32_GENERIC \
    USER_C_MODULES=../../../../gc9a01_mpy/src/micropython.cmake \
    FROZEN_MANIFEST=../../../../../../gc9a01_mpy/manifest.py \   
    erase deploy



```