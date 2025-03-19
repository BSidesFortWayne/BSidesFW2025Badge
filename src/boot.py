# boot.py -- run on boot-up
import machine


frequency = 240_000_000

if machine.freq() != frequency:
    machine.freq(frequency)


