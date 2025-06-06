# Custom Badge Firmware

Our custom badge firmware binary was developed with C modules and drivers already compiled into the MicroPython source code. This firmware is required for the CTF challenges as many of the challenges rely on custom C compiled into the MicroPython image in order to operate.

**BSFWCustom_firmware_SPIRAM_with_GC9A01.bin** - This binary includes MicroPython 1.26.0, our custom Badge Challenges, and the Russ Hughes GC9A01 MicroPython C-Based Display driver.

The binary can be easily flashed to your board with the following commands:

```shell
uv run esptool.py erase_flash
uv run esptool.py --baud 460800 write_flash 0x1000 <location_of_your_downloaded_bin_file>

# e.g.
uv run esptool.py --baud 460800 write_flash 0x1000 ~/Downloads/BSFWCustom_firmware_SPIRAM_with_GC9A01.bin
```
