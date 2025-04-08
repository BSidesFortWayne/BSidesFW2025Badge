from machine import Pin, PWM
from time import sleep_ms

# Buzzer setup
buzzer_pin = 12
buzzer = PWM(Pin(buzzer_pin))

# Constants
BPM = 120
Q = int(60000 / BPM)  # quarter note duration in ms
H = 2 * Q
E = Q // 2
S = Q // 4
W = 4 * Q

# Define the notes (some examples)
C4 = 261.63
Db4 = 277.18
D4 = 293.66
Eb4 = 311.13
E4 = 329.63
F3 = 174.61
F4 = 349.23
Gb4 = 369.99
G4 = 392.00
Ab3 = 207.65
Ab4 = 415.30
LA3 = 220.00
LA4 = 440.00
Bb3 = 233.08
Bb4 = 466.16
B3 = 246.94
C5 = 523.25
Db4 = 277.18
D4 = 293.66
Eb4 = 311.13
Db4 = 277.18

def mytone(freq, duration):
    if freq > 0:
        buzzer.freq(int(freq))
        buzzer.duty(512)  # duty cycle: 50%
    else:
        buzzer.duty(0)
    sleep_ms(duration)
    buzzer.duty(0)

# You can directly run this in a while True loop or as a test
def play_melody():
    mytone(LA3, Q) 
    mytone(LA3, Q)
    mytone(LA3, Q)
    mytone(F3, E + S)
    mytone(C4, S)
    
    mytone(LA3, Q)
    mytone(F3, E + S)
    mytone(C4, S)
    mytone(LA3, H)

    mytone(E4, Q) 
    mytone(E4, Q)
    mytone(E4, Q)
    mytone(F4, E + S)
    mytone(C4, S)
    
    mytone(Ab3, Q)
    mytone(F3, E + S)
    mytone(C4, S)
    mytone(LA3, H)

    mytone(LA4, Q)
    mytone(LA3, E + S)
    mytone(LA3, S)
    mytone(LA4, Q)
    mytone(Ab4, E + S)
    mytone(G4, S)
    
    mytone(Gb4, S)
    mytone(E4, S)
    mytone(F4, E)
    sleep_ms(E)
    mytone(Bb3, E)
    mytone(Eb4, Q)
    mytone(D4, E + S)
    mytone(Db4, S)

    mytone(C4, S)
    mytone(B3, S)
    mytone(C4, E)
    sleep_ms(E)
    mytone(F3, E)
    mytone(Ab3, Q)
    mytone(F3, E + S)
    mytone(LA3, S)

    mytone(C4, Q)
    mytone(LA3, E + S)
    mytone(C4, S)
    mytone(E4, H)

    mytone(LA4, Q)
    mytone(LA3, E + S)
    mytone(LA3, S)
    mytone(LA4, Q)
    mytone(Ab4, E + S)
    mytone(G4, S)
    
    mytone(Gb4, S)
    mytone(E4, S)
    mytone(F4, E)
    sleep_ms(E)
    mytone(Bb3, E)
    mytone(Eb4, Q)
    mytone(D4, E + S)
    mytone(Db4, S)

    mytone(C4, S)
    mytone(B3, S)
    mytone(C4, E)
    sleep_ms(E)
    mytone(F3, E)
    mytone(Ab3, Q)
    mytone(F3, E + S)
    mytone(C4, S)

    mytone(LA3, Q)
    mytone(F3, E + S)
    mytone(C4, S)
    mytone(LA3, H)

    sleep_ms(2 * H)

# Run once or in a loop
play_melody()