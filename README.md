# BSidesFW2025Badge

BSides Fort Wayne Badge Programming

# Development: Getting Started

### Tools
The python packages in this repository are managed by `uv`. The repository structure is as follows

- `.venv`: This folder will be installed when you set up the python virtual environment with uv
- `.vscode`: Vscode specific settings for this project
- `schematics`: Board schematics as PDF
- `src`: The embedded code for deployment on the target
- `STLs`: Screen bezels, supports, and PCB STLs
- `typings`: Custom typings for the VSCode Python Language Server in order to get better typehints and support for the micropython code


### Setup
Install `uv` (https://docs.astral.sh/uv/getting-started/installation/) based on your OS of choice. If on Windows, you may have a better development experience in `WSL` if you can provide access to the ESP32 chip to the WSL instance (https://learn.microsoft.com/en-us/windows/wsl/connect-usb). However, `uv` and `mpremote` both work on Windows so you can also develop natively

###

Once you have `uv` setup, you can simply run

```shell
uv sync
```

to get the virtual environment set up. Once you plug in and turn on your dev board, you need to give permissions (Linux only)

```shell
sudo chmod a+x /dev/ttyUSB0
```

At this point, you will need to flash our base image, which is here: https://github.com/russhughes/gc9a01_mpy/raw/refs/heads/main/firmware/ESP32_GENERIC/firmware_SPIRAM_8MiB.bin

You can erase the flash and then flash the board with the above image with the following commands

```shell
uv run esptool.py erase_flash
uv run esptool.py --baud 460800 write_flash 0x1000 <location_of_your_downloaded_bin_file>

# e.g.
uv run esptool.py --baud 460800 write_flash 0x1000 ~/Downloads/firmware_SPIRAM_8MiB.bin
```

And then you can either mount the `src` directory for the board and start in a REPL

```shell
uv run mpremote mount src
```

Or deploy the source to the board directly

```shell
uv run mpremote cp -r src/* :
```

# Technical Specifications V2

This section describes the technical specifications of the board to aid in development.

## Schematic Overview

Within the [schematics/BSides Badge V2 Schematic.pdf](https://github.com/commputethis/BSidesFW2025Badge/blob/68bb887bfc6d0544537c8bf179ed645db8c0f13b/schematics/BSides%20Badge%20V2%20Schematic.pdf) you will find the electrical schematic of the device including the part numbers and connections between components identified as net labels. Each section of the schematic will be described below and applicable datasheets will be linked.

### ESP32-WROVER-E-N8R8

This section contains the ESP32-WROVER-E-N8R8 itself, the decoupling capacitors, the pullup resistors required for operation of the I2C Bus, and the net labels associated with the GPIO pins of the ESP32. 
The ESP32-WROVER-E-N8R8 has a 240Mhz Dual Core processor with 8Mb of Flash and 8Mb of RAM available on the SPI bus.

Datasheets:
https://www.espressif.com.cn/sites/default/files/documentation/esp32-wrover-e_esp32-wrover-ie_datasheet_en.pdf

### USB-Serial

This board uses a CH340C USB to Serial chip to allow for programming via USB-C connector. When connected to USB-C your computer should detect a USB to Serial interface resulting in the creation of a COM port much like any ESP32 or Arduino style device.

### USB-C

This section contains the USB-C shell connector and associated netlabels. CC1 and CC2 are connected to 5.1k resistors to request basic 5V low power from the USB-C device connected. DP and DN data connectors are connected to the CH340C to facilitate communication with the ESP32 via the UART.

### WS2812B

This section contains the 7 RGB LEDs that are connected to IO26. Nothing much more to say about this... Treat it like a small LED strip.

Note: The 5V switching power supply is present on the V2 schematic, but has been disabled. The red jumper on H3 is providing 3.3V to the 5V bus. There is no need to enable the 5v power supply, stuff just works.

https://www.lcsc.com/product-detail/RGB-LEDs-Built-in-IC_Worldsemi-WS2812B-B-T_C2761795.html

### RTS/DTR Circuit

This section contains a dual transistor package which is used to place the ESP32 into programming mode and reset mode based on the RTS/DTR output of the CH340C driven by the attached programming software application.

### Boot/Function Buttons

These are the 4 buttons across the top of the device to the right of the ESP32 and two gaming buttons. SW1 is dual purpose. During normal operation, it serves as a simple button attached to IO0. However, IO0 is a strapping pin dedicated to placing the ESP32 into the boot (programming) mode. If SW1 is held during startup, the device will be manually placed into boot mode. This should not be required during normal programming sessions as the RTS/DTR circuit should handle this function, but it is available if needed in special circumstances. SW2, SW3, SW4, SW7, and SW8 are basic buttons connected to a PCA9535 IO expander at address 0x20 on the I2C bus. All lines are pulled high and are active low.

SW1 > IO0

SW2 > IO1_2

SW3 > IO1_1

SW4 > IO1_0

SW7 > IO0_2

SW8 > IO0_1

### Reset Button

Connected to the EN pin of the ESP32. Pressing this will reset the device.

### LIS3DHTR Accelerometer I2C Address 0x18

This section contains the accelerometer (LIS3DHTR) and the associated connections. The datasheet is linked for reference, and that reference will probably be needed. The I2C data lines are connected to IO22 (SCL) and IO21 (SDA) on the ESP32, and the accelerometer can be accessed at I2C address 0x18. IO34 is also dedicated to a programmable interrupt pin on the accelerometer for possible use. An example of this device would be for power saving. If no motion is detected for an interval, the device could be put into a reduced power state and then later woken up using the interrupt pin. Of course, there are plenty of other fun things that can be accomplished using the three-axis output of the accelerometer. The unused interrupts and ADC inputs are wired to the expansion headers for future use.

Datasheet:

https://www.st.com/resource/en/datasheet/lis3dh.pdf

### Battery Monitor

This is a very simple voltage divider that represents the current voltage of the LIPO 3.7v nominal battery. It is read via ADC1 on the Accelerometer on the I2C bus. The divider ratio is 27:100, resulting in a fully charged battery at 4.2v sending 3.3V to ADC1, and a fully discharged battery at 3.0v will result in 2.36v at ADC1. Admittedly, this is not the best method of determining battery charge status, but it's better than nothing, and with some simple code to average the readings then, it can be effective at gauging basic SOC levels.

### DW01A Battery Protection

This is a safety feature to prevent damage to the battery due to overcharging or over-discharging. It will disable the battery in the event of any anomaly. It's a very commonly used circuit to manage single-cell lithium battery safety.

### Battery Charger TP4056

This is a basic single cell lithium battery charger circuit. It will charge at up to ~900ma using the power delivered from the USB-C VBUS and will manage the charging of the lithium cell. Two LEDs indicate charge status. Red = Charging, Green = Fully Charged.

### Boost Buck 3V3

This is the primary switching power converter and takes its input from the VCC network (Post power switch, battery protection, and fuse) and converts that into a stable 3.3V for the board Components. This power module (TPS63060DSCR) is a boost buck module and can accept input voltages in a wide range to deliver a consistent 3.3V output. This module is running anytime the power switch is in the on position and a battery is connected. 

Note: This device is not designed to operate without a battery. The battery provides voltage stability that the boost buck converter requires for reliable operation. Operating the device from USB power with no battery is not recommended and will result in undesirable power fluctuations.

### Voltage Boost 3.3V to 5V

No longer used.

### Power Switch

Simple... Its a switch. Turn it on to use it.

### Display Headers

These are the 7pin female headers that the screens plug into as well as transistors that control power to the displays. The DISP_EN network is connected to IO32. IO32 controls the power status of the displays. Bringing IO32 high will enable the displays, and bringing it low will disable the displays can can be used to save power when not in use. By default IO32 is pulled low and the displays will be normally off.

The Screens are both connected to the SPI data bus, and can operate independantly via software using the Data Control, Reset, and Chip Select Pins. Pinouts below...

Common Pins for SPI Bus:

MOSI > IO23

CLK > IO18

Screen 1 Pins:

DC1 > IO19

RST1 > IO14

CS1 > IO33

Screen 2 Pins:

DC2 > IO25

RST2 > IO27

CS2 > IO13

### Speaker

Yes... V2 has audio! There is a "speaker" (really a variable frequency buzzer) You can send tones by adjusting the PWM frequency and vary the volume by adjusting the PWM duty cycle. This is connected to IO15 of the ESP32. Datasheet below:

https://www.lcsc.com/product-detail/Buzzers_HYDZ-HYG-7525A-5027_C18623827.html

### Expansion Headers

V2 contains two expansion headers. In V3 these will not be populated with headers and will be available to anyone who wants to hack these devices and use IO that is not used by anything else on the board.

### Input/Output Expander 0x20

This is a PCA9535 IO expander at address 0x20 on the I2C bus IO22 (SCL) and IO21 (SDA). The PCA9535 provides an additional 16 GPIO lines via the I2C bus and in this application is used to read the status of buttons. For details about the buttons refer to the Boot/Function Buttons section. The unused IO lines are wired to the expansion headers for future use.


## GPIO Pin Assignments

IO0    		Boot/Button 1 (Strapping)

IO2    		(Strapping) Not Connected

IO4    		(Strapping) Not Connected

IO5    		(Strapping) Not Connected

IO12   		(Strapping) Not Connected

IO13   		CS2 

IO14   		RST1

IO15   		(Strapping) Speaker

IO18   		CLK

IO19   		DC1

IO21   		I2C SDA

IO22   		I2C SCL

IO23   		MOSI

IO25   		DC2

IO26   		WS2812B

IO27   		RST2

IO32   		DISP_EN

IO33   		CS1 

IO34   		Accelerometer Interrupt

IO35   		Not Connected

