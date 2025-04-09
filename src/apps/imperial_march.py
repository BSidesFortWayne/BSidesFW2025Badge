from machine import Pin, PWM
from time import sleep_ms
from apps.app import BaseApp

class ImperialMarch(BaseApp):
    name = "Imperial March"
    def __init__(self, buzzer_pin=15, bpm=100):
        self.bpm = bpm
        self.Q = int(60000 / bpm)
        self.H = 2 * self.Q
        self.E = self.Q // 2
        self.S = self.Q // 4

        self.buzzer = PWM(Pin(buzzer_pin))
        self.buzzer.duty(0)

        self.notes = {
            'A3': 220, 'A4': 440, 'A5': 880,
            'C4': 262, 'C5': 523, 'C#4': 277, 'C#5': 554,
            'D4': 294, 'D5': 587,
            'E4': 330, 'E5': 659,
            'F4': 349, 'F5': 698,
            'G4': 392, 'G5': 784,
            'G#4': 415, 'G#5': 831,
            'REST': 0
        }

        # Full Imperial March melody, with corresponding note durations
        self.melody = [
            ('A4', self.Q), ('A4', self.Q), ('A4', self.Q),
            ('F4', self.E), ('C5', self.S),
            ('A4', self.Q), ('F4', self.E), ('C5', self.S), ('A4', self.H),

            ('E5', self.Q), ('E5', self.Q), ('E5', self.Q),
            ('F5', self.E), ('C5', self.S),
            ('G#4', self.Q), ('F4', self.E), ('C5', self.S), ('A4', self.H),

            # Pause after first section
            ('REST', self.H),

            ('A5', self.Q), ('A4', self.E), ('A4', self.S),
            ('A5', self.Q), ('G#5', self.E), ('G5', self.S),
            ('F5', self.S), ('E5', self.S), ('F5', self.E),
            ('REST', self.E),

            ('A4', self.E), ('C5', self.Q), ('A4', self.E),
            ('C5', self.Q), ('E5', self.H),

            # Next section
            ('A4', self.Q), ('A4', self.Q), ('A4', self.Q),
            ('F4', self.E), ('C5', self.S),
            ('A4', self.Q), ('F4', self.E), ('C5', self.S), ('A4', self.H),

            ('E5', self.Q), ('E5', self.Q), ('E5', self.Q),
            ('F5', self.E), ('C5', self.S),
            ('G#4', self.Q), ('F4', self.E), ('C5', self.S), ('A4', self.H),

            # Section with variation
            ('A5', self.Q), ('A4', self.E), ('A4', self.S),
            ('A5', self.Q), ('G#5', self.E), ('G5', self.S),
            ('F5', self.S), ('E5', self.S), ('F5', self.E),
            ('REST', self.E),

            ('A4', self.E), ('C5', self.Q), ('A4', self.E),
            ('C5', self.Q), ('E5', self.H),

            # Final repeat section
            ('A4', self.Q), ('A4', self.Q), ('A4', self.Q),
            ('F4', self.E), ('C5', self.S),
            ('A4', self.Q), ('F4', self.E), ('C5', self.S), ('A4', self.H),

            ('E5', self.Q), ('E5', self.Q), ('E5', self.Q),
            ('F5', self.E), ('C5', self.S),
            ('G#4', self.Q), ('F4', self.E), ('C5', self.S), ('A4', self.H),
            
            # End
            ('REST', self.H),
        ]

    def tone(self, note, duration):
        freq = self.notes.get(note, 0)
        if freq > 0:
            self.buzzer.freq(freq)
            self.buzzer.duty(512)
        else:
            self.buzzer.duty(0)  # pause

        sleep_ms(duration)
        self.buzzer.duty(0)
        sleep_ms(30)  # small gap between notes

    def play(self):
        for note, duration in self.melody:
            self.tone(note, duration)