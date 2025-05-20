# Badger 2040

This is a work in progress and more information will be added soon.

- [Badger 2040](#badger-2040)
  - [Summary](#summary)
  - [Requirements](#requirements)
  - [Badger GUI Script](#badger-gui-script)
  - [Create Badge Script](#create-badge-script)
  - [Badge Script](#badge-script)
  - [BSides Fort Wayne Logo](#bsides-fort-wayne-logo)
  - [Badge Logo](#badge-logo)
  - [Badge Text File](#badge-text-file)

## Summary

This is a project to program Badger 2040s during check in at the BSides Fort Wayne 2023 conference.  At least that is what it has started as.  It is possible it will morph into something greater.  The scripts are python.  All testing has been done on Linux (Ubuntu and Raspberry Pi OS)

## Requirements

The following need to be installed:

- python3
- pip3
- pil
- tkinter
- rshell

In addition to the above installs, the user nees to be part of the "dialout" group.

## Badger GUI Script

[badger_gui.py](/code/badger_gui.py) is a script to have a fullscreen form to fill out to configure the badge.  It will give a confirmation after the script is completed and then clear the fields to be ready for the next badge.  To exit the script, press Alt+F4.

## Create Badge Script

[create_badge.py](/code/create_badge.py) is a script that runs in the command line using agruments for name, company, and status.  If name or company are not provided, then they will be blank.  If the status is not provided, then it will default to "Attendee."

## Badge Script

[badge.py](/code/badge.py) is a script from the Badger 2040 Examples folder with the "DETAILS_TEXT_SIZE" variable modified from .5 to .45 so the "BSides Fort Wayne 2023" will fit in the box at the bottom of the badge.  This script is transferred to the Badger 2040 by both scripts above.

## BSides Fort Wayne Logo

[BSidesLogo.png](/images/BSidesLogo.png) is the logo from the BSides Fort Wayne website and it gets resized and will show up on the form created by the Badger Gui Script.  This image does NOT get transferred to the Badger 2040.

## Badge Logo

[BadgeLogo.jpg](/images/BadgeLogo.jpg) is transferred to the Badger 2040 to be used on the badge.

## Badge Text File

The badge.txt file gets created by the badge.py and create_badge.py scripts and is then transferred to the Badger 2040 to be used on the badge.
