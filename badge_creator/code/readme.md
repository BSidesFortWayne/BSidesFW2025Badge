# How to run the scripts

This assumes the machine the scripts are being run from already have the pre-reqs installed (as shown in [setup.md](../setup.md)).

## badger_gui.py

Before running the script, one must set the variables in the script.  To do so, open the script in a text editor.  There is a list of Global variables at the top which need to be verified.  Most do not need to be modified for BSides, but at a minimum, the local file location(s) need updated for the machine it is being run from.

The script is run as follows from the terminal:

Example using default variable values:

``` python
python3 badger_gui.py
```

Example defining the localpath variable value:

``` python
python3 "badger_gui.py" --localpath "/home/registration/Documents/badge_creator/"
```
