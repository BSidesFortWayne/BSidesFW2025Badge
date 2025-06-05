# Badge Creator

- [Badge Creator](#badge-creator)
  - [Summary](#summary)
  - [Requirements](#requirements)
  - [Badger GUI Script](#badger-gui-script)
  - [BSides Fort Wayne Logo](#bsides-fort-wayne-logo)
  - [Badge Logo](#badge-logo)

## Summary

This is to program Badger 2040s or Gigtel Badges (Custom badge for BSides FW sponsored by Gigtel) during check-in at the BSides Fort Wayne Conference.  The scripts are python.  All testing has been done on Ubuntu.

## Requirements

The following need to be installed (done using the [reg_station_setup.sh](reg_station_setup.sh) script):

- python3
- pip3
- pil
- tkinter
- rshell
- uv
- pipx
- mpremote

In addition to the above installs, the user nees to be part of the "dialout" group.

## Badger GUI Script

[badger_gui.py](/code/badger_gui.py) is a script to have a fullscreen form to fill out to configure the badge.  It will give a confirmation after the script is completed and then clear the fields to be ready for the next badge.  To exit the script, press Alt+F4.

## BSides Fort Wayne Logo

[BSidesLogo.png](/images/BSidesLogo.png) is the logo from the BSides Fort Wayne website and it gets resized and will show up on the form created by the Badger Gui Script.  This image does NOT get transferred to the Badge.

## Badge Logo

[BadgeLogo.jpg](/images/BadgeLogo.jpg) is transferred to the Badger 2040 to be used on the badge.
