# BSidesFW2025Badge
BSides Fort Wayne Badge Programming

This is able to display an image on both of the displays, and turn on the 4 lights next to the displays. It has some problems though. Either the library I am using is inefficient, another processor needs to be used, or both. Right now, it takes ~10 seconds to draw an image on one of the displays. I initially was using the library, [TFT_eSPI](https://github.com/Bodmer/TFT_eSPI). This library worked fine, except the DC, and RST pins for both the displays should be connected in parallel instead of being assigned individual GPIO pins. This will be fixed in version 2 of the board. TFT_eSPI does not support multiple displays, but in the setup I described, it can work by setting the CS pin to high for the display you want to draw to. I was able to get the TFT_eSPI library working for 1 display, which did work faster, but I never tested drawing an image. TFT_eSPI can also be used with [LVGL](https://lvgl.io). Right now, it is using the library, [Adafruit GFX](https://github.com/adafruit/Adafruit-GFX-Library).

# Technical Specifications

This section describes the technical specifications of the board to aid in development.

## Schematic Overview

Within the schematics/BSides Badge V1 Schematic.pdf you will find the electrical schematic of the device including the part numbers and connections between components identified as net labels. Each section of the schematic will be described below and applicable datasheets will be linked.

### ESP32-WROOM-32-N4

This section contains the ESP32-WROOM-32-N4 itself, the decoupling capacitors, the pullup resistors required for operation of the I2C Bus, and the net labels associated with the GPIO pins of the ESP32. 

Note: In version 1 we are using the ESP32-WROOM-32-N4, version 2 is planned to use the ESP32-WROVER-E-N8R8 to allow more PSRAM for use in displaying images and animations without needing to read from flash as often.

Datasheets:

https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32_datasheet_en.pdf
https://www.espressif.com.cn/sites/default/files/documentation/esp32-wrover-e_esp32-wrover-ie_datasheet_en.pdf

### USB-Serial

This board uses a CH340C USB to Serial chip to allow for programming via USB-C connector. When connected to USB-C your computer should detect a USB to Serial interface resulting in the creation of a COM port much like any ESP32 or Arduino style device.

### USB-C

This section contains the USB-C shell connector and associated netlabels. CC1 and CC2 are connected to 5.1k resistors to request basic 5V low power from the USB-C device connected. DP and DN data connectors are connected to the CH340C to facilitate communication with the ESP32 via the UART.

### WS2812B

This section contains the 4 RGB LEDs that are connected to IO26. Nothing much more to say about this... Treat it like a small LED strip.

Note: The 5V switching power supply is disabled by default as a power management feature. It's operation is described in the Voltage Boost 3.3V to 5V section.

https://www.lcsc.com/product-detail/RGB-LEDs-Built-in-IC_Worldsemi-WS2812B-B-T_C2761795.html

### RTS/DTR Circuit

This section contains a dual transistor package which is used to place the ESP32 into programming mode and reset mode based on the RTS/DTR output of the CH340C driven by the attached programming software application.

### Boot/Function Buttons

These are the 4 buttons across the top of the device to the right of the ESP32. SW1 is dual purpose. During normal operation, it serves as a simple button attached to IO0. However, IO0 is a strapping pin dedicated to placing the ESP32 into the boot (programming) mode. If SW1 is held during startup, the device will be manually placed into boot mode. This should not be required during normal programming sessions as the RTS/DTR circuit should handle this function, but it is available if needed in special circumstances. SW2, SW3, and SW4 are basic buttons connected directly to GPIO lines. All lines are pulled high and are active low.

SW1 > IO0

SW2 > IO33

SW3 > IO35

SW4 > IO34

### Reset Button

Connected to the EN pin of the ESP32. Pressing this will reset the device.

### LIS3DHTR Accelerometer I2C Address 0x18

This section contains the accelerometer (LIS3DHTR) and the associated connections. The datasheet is linked for reference, and that reference will probably be needed. The I2C data lines are connected to IO25 (SCL) and IO17 (SDA) on the ESP32, and the accelerometer can be accessed at I2C address 0x18. IO13 is also dedicated to a programmable interrupt pin on the accelerometer for possible use. An example of this device would be for power saving. If no motion is detected for an interval, the device could be put into a reduced power state and then later woken up using the interrupt pin. Of course, there are plenty of other fun things that can be accomplished using the three-axis output of the accelerometer.

Datasheet:

https://www.st.com/resource/en/datasheet/lis3dh.pdf

### Battery Monitor

This is a very simple voltage divider that represents the current voltage of the LIPO 3.7v nominal battery. It is read into the ESP32 on IO32. The divider ratio is 27:100, resulting in a fully charged battery at 4.2v sending 3.3V to IO32, and a fully discharged battery at 3.0v will result in 2.36v at IO32. Admittedly, this is not the best method of determining battery charge status, but it's better than nothing, and with some simple code to average the readings then, it can be effective at gauging basic SOC levels.

### DW01A Battery Protection

This is a safety feature to prevent damage to the battery due to overcharging or over-discharging. It will disable the battery in the event of any anomaly. It's a very commonly used circuit to manage single-cell lithium battery safety.

### Battery Charger TP4056

This is a basic single cell lithium battery charger circuit. It will charge at up to ~900ma using the power delivered from the USB-C VBUS and will manage the charging of the lithium cell. Two LEDs indicate charge status. Red = Charging, Green = Fully Charged.

### Boost Buck 3V3

This is the primary switching power converter and takes its input from the VCC network (Post power switch, battery protection, and fuse) and converts that into a stable 3.3V for the board Components. This power module (TPS63060DSCR) is a boost buck module and can accept input voltages in a wide range to deliver a consistent 3.3V output. This module is running anytime the power switch is in the on position and a battery is connected. 

Note: This device is not designed to operate without a battery. The battery provides voltage stability that the boost buck converter requires for reliable operation. Operating the device from USB power with no battery is not recommended and will result in undesirable power fluctuations.

### Voltage Boost 3.3V to 5V

This switching power supply is provided for the operation of the WS2812B RGB LEDs, which require 5V for reliable operation. The input for this module is 3.3V from the Boost Buck converter and the output is 5V. This power supply module is controlled via IO16 net label 5VEN. When IO16 is pulled high the power supply will be enabled and will output 5V. Basically if you want to use the RGB LEDs, then pull IO16 high to enable the power. If you want to save power then set IO16 low.

### Power Switch

Simple... Its a switch. Turn it on to use it.

### Screen Headers

Forgot to label this section, but these are the 7pin female headers that the screens plug into.

The Screens are both connected to the SPI data bus, and can operate independantly via software using the Data Control, Reset, and Chip Select Pins. Pinouts below...

Common Pins for SPI Bus:

MOSI > IO23

CLK > IO18

Screen 1 Pins:

DC1 > IO22

RST1 > IO14

CS1 > IO5

Screen 2 Pins:

DC2 > IO21

RST2 > IO27

CS2 > IO4



## GPIO Pin Assignments

IO0    Boot/Button 1

IO2    Strapping

IO4    CS2

IO5    CS1

IO12   Strapping

IO13   Accelerometer Interrupt

IO14   RST1

IO15   Strapping

IO16   5VEN

IO17   I2C SDA

IO18   CLK

IO19   No Connection

IO21   DC2

IO22   DC1

IO23   MOSI

IO25   I2C SCL

IO26   WS2812B

IO27   RST2

IO32   Battery Monitor

IO33   Button 2

IO34   Button 4

IO35   Button 3
