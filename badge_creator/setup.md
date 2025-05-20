# Setup Linux to be able to run these scripts

This assumes Linux (either Ubuntu or Raspberry Pi OS) is already installed.

- [Setup Linux to be able to run these scripts](#setup-linux-to-be-able-to-run-these-scripts)
  - [Install Python3](#install-python3)
  - [Install pip3](#install-pip3)
  - [Install pil](#install-pil)
  - [Install Tkinter](#install-tkinter)
  - [Install rshell](#install-rshell)
  - [Add user to the dialout group](#add-user-to-the-dialout-group)

## Install Python3

Check to see if Python3 is installed by running the following from terminal:  

- ```python3 -V```

If the version isn't returned, then run the following:

- ```sudo apt install python3```

## Install pip3

Check to see if pip3 is installed by running the following from terminal:

- ```pip3 -V```

If the version isn't returned, then run the following:

- ```sudo apt install python3-pip```

## Install pil

Install pil and pil.imagetk using the following from terminal:

- ```sudo apt install python3-pil pythong3-pil.imagetk```

## Install Tkinter

Install Tkinter using the following from terminal:

- ```sudo apt install python3-tk```

## Install rshell

Install rshell using the following from terminal:

- ```sudo pip3 install rshell```

## Add user to the dialout group

Add user to the dialout group so it can communicate with the Badger 2040 through the serial port (USB). Use the following from terminal (replace username with the user the script will be run by):

- ```sudo usermod -a -G dialout username```
