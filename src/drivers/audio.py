import asyncio
import machine
import json

from drivers.base import Driver

AUDIO_STOPPED = 0
AUDIO_PLAYING = 1
AUDIO_PAUSED = 2

class Speaker(Driver):
    def __init__(self):
        super().__init__()
        self.pwm_pin = machine.Pin(15)
        self.pwm = machine.PWM(self.pwm_pin, freq=50, duty_u16=200)
        self.pwm.duty_u16(0)
        
        self.speed = 1
        self.state = AUDIO_STOPPED
        self.current_song_task = None
        self.current_song = None
        self.duty = 30

    def resume_song(self):
        self.state = AUDIO_PLAYING

    def start_song(self, song_id, repeat=False):
        if self.current_song == song_id:
            print(f"Already playing song {song_id}")
            return

        song_file = open(f'songs/{song_id}.json')

        song = json.loads(song_file.read())

        song_file.close()

        if self.state == AUDIO_PLAYING:
            self.state = AUDIO_STOPPED
        
        self.current_song = song_id

        self.current_song_task = asyncio.create_task(self._play_song(song, repeat))

    def stop_song(self):
        self.state = AUDIO_STOPPED

    def pause_song(self):
        self.state = AUDIO_PAUSED

    async def _play_song(self, song, repeat=False):
        self.duration = self.get_song_duration(song)
        print(f"Song Duration Is: {self.duration}")
        self.state = AUDIO_PLAYING
        while self.state != AUDIO_STOPPED:
            for note, duration in song:
                if self.state == AUDIO_STOPPED:
                    break
                
                if note != 'R':
                    self.pwm.freq(int(note/2))
                    self.pwm.duty(self.duty)
                else:
                    self.pwm.duty(0)

                await asyncio.sleep(duration / self.speed)
                self.pwm.duty(0)
                await asyncio.sleep(0.01)
                if self.state == AUDIO_PAUSED:
                    while self.state == AUDIO_PAUSED:
                        await asyncio.sleep(0.1)
            if not repeat:
                break
        # self.state = AUDIO_STOPPED
        self.current_song = None


    def get_song_duration(self, song):
        duration = 0
        for _, d in song:
            duration += d
        return duration
