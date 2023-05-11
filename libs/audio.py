import io
from gtts import gTTS
import threading
from pygame import mixer
from libs import volume_control, yt
import time

class Audio:
    def __init__(self):
        self.mixer = mixer
        self.mixer.init()
        self.music_stream = None
        self.volume_control = volume_control.VolumeControl(self)

    def play(self, audio, cursor=0):
        mixer.music.load(audio)
        mixer.music.play(start=cursor)

    def play_music(self, query):
        if self.music_stream:
            self.music_stream.stop()
            self.music_stream.thread.join()
        self.music_stream = yt.AudioStream(query)
        self.music_stream.set_volume(self.volume_control.get_volume())
        self.music_stream.start()
        print("Playing " + self.music_stream.query)

    def speak(self, text: str):
        sentences = text.split(". ")
        audios = [None] * len(sentences)
        threads = []

        def callback(sentence, position):
            tts = gTTS(sentence)
            tts_audio = io.BytesIO()
            tts.write_to_fp(tts_audio)
            tts_audio.seek(0)
            audios[position] = tts_audio

        for position, sentence in enumerate(sentences):
            thread = threading.Thread(target=callback, args=(sentence, position))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        combined_audio_bytesio = io.BytesIO()

        for audio_bytesio in audios:
            combined_audio_bytesio.write(audio_bytesio.getbuffer())

        combined_audio_bytesio.seek(0)
        self.play(combined_audio_bytesio)