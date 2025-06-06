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
# This will deploy all src, but mpremote will check the hash of the files to determine 
uv run mpremote cp -r src/* :
```

Here are some other useful patterns with `mpremote`

```shell
# when developing and iterating quickly, we can use this to deploy the file you are working on and then running `main` from local
# in one command
uv run mpremote cp -r src/apps/analog_clock.py + run main.py
```