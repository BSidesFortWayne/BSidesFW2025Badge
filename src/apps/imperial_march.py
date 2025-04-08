from machine import Pin, PWM
from time import sleep_ms
from apps.app import BaseApp

class Imperial_March(BaseApp):
    name = "Imperial March"
    def __init__(self, buzzer_pin=12, bpm=120):
        self.bpm = bpm
        self.Q = int(60000 / self.bpm)
        self.H = 2 * self.Q
        self.E = self.Q // 2
        self.S = self.Q // 4
        self.W = 4 * self.Q

        self.buzzer = PWM(Pin(buzzer_pin))
        self.buzzer.duty(0)

        self.notes = {
            'C4': 261.63, 'Db4': 277.18, 'D4': 293.66, 'Eb4': 311.13, 'E4': 329.63,
            'F3': 174.61, 'F4': 349.23, 'Gb4': 369.99, 'G4': 392.00,
            'Ab3': 207.65, 'Ab4': 415.30, 'LA3': 220.00, 'LA4': 440.00,
            'Bb3': 233.08, 'Bb4': 466.16, 'B3': 246.94, 'C5': 523.25,
            'Eb4': 311.13, 'D4': 293.66, 'Db4': 277.18, 'C4': 261.63
        }

    def mytone(self, freq, duration):
        if freq > 0:
            self.buzzer.freq(int(freq))
            self.buzzer.duty(512)
        else:
            self.buzzer.duty(0)
        sleep_ms(duration)
        self.buzzer.duty(0)

    def play(self):
        n = self.notes
        Q, H, E, S = self.Q, self.H, self.E, self.S

        self.mytone(n['LA3'], Q)
        self.mytone(n['LA3'], Q)
        self.mytone(n['LA3'], Q)
        self.mytone(n['F3'], E + S)
        self.mytone(n['C4'], S)

        self.mytone(n['LA3'], Q)
        self.mytone(n['F3'], E + S)
        self.mytone(n['C4'], S)
        self.mytone(n['LA3'], H)

        self.mytone(n['E4'], Q)
        self.mytone(n['E4'], Q)
        self.mytone(n['E4'], Q)
        self.mytone(n['F4'], E + S)
        self.mytone(n['C4'], S)

        self.mytone(n['Ab3'], Q)
        self.mytone(n['F3'], E + S)
        self.mytone(n['C4'], S)
        self.mytone(n['LA3'], H)

        self.mytone(n['LA4'], Q)
        self.mytone(n['LA3'], E + S)
        self.mytone(n['LA3'], S)
        self.mytone(n['LA4'], Q)
        self.mytone(n['Ab4'], E + S)
        self.mytone(n['G4'], S)

        self.mytone(n['Gb4'], S)
        self.mytone(n['E4'], S)
        self.mytone(n['F4'], E)
        sleep_ms(E)
        self.mytone(n['Bb3'], E)
        self.mytone(n['Eb4'], Q)
        self.mytone(n['D4'], E + S)
        self.mytone(n['Db4'], S)

        self.mytone(n['C4'], S)
        self.mytone(n['B3'], S)
        self.mytone(n['C4'], E)
        sleep_ms(E)
        self.mytone(n['F3'], E)
        self.mytone(n['Ab3'], Q)
        self.mytone(n['F3'], E + S)
        self.mytone(n['LA3'], S)

        self.mytone(n['C4'], Q)
        self.mytone(n['LA3'], E + S)
        self.mytone(n['C4'], S)
        self.mytone(n['E4'], H)

        self.mytone(n['LA4'], Q)
        self.mytone(n['LA3'], E + S)
        self.mytone(n['LA3'], S)
        self.mytone(n['LA4'], Q)
        self.mytone(n['Ab4'], E + S)
        self.mytone(n['G4'], S)

        self.mytone(n['Gb4'], S)
        self.mytone(n['E4'], S)
        self.mytone(n['F4'], E)
        sleep_ms(E)
        self.mytone(n['Bb3'], E)
        self.mytone(n['Eb4'], Q)
        self.mytone(n['D4'], E + S)
        self.mytone(n['Db4'], S)

        self.mytone(n['C4'], S)
        self.mytone(n['B3'], S)
        self.mytone(n['C4'], E)
        sleep_ms(E)
        self.mytone(n['F3'], E)
        self.mytone(n['Ab3'], Q)
        self.mytone(n['F3'], E + S)
        self.mytone(n['C4'], S)

        self.mytone(n['LA3'], Q)
        self.mytone(n['F3'], E + S)
        self.mytone(n['C4'], S)
        self.mytone(n['LA3'], H)

        sleep_ms(2 * H)

# Usage
app = App()
app.play()
