import json
import vosk
import pyaudio

class Recognizer:

    def __init__(self,
                 audio,
                 model_path="vosk-model-small-en-us-0.15",
                 input_device_name="Blue Snowball: USB Audio (hw:1,0)",
                 sample_rate=16000,
                 prefix="computer"):
        self.audio = audio
        model = vosk.Model(model_path)
        print("Model loaded")
        self.buffer_size = 4096
        self.prefix = prefix
        self.listening = False
        self.auto_listen = False
        self.gpt_models = ("text-curie-001", "gpt-3.5-turbo")
        self.gpt_model = 0
        self.rec = vosk.KaldiRecognizer(model, sample_rate)
        print("Recognizer created")
        p = pyaudio.PyAudio()

        input_device_index = None
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev['name'] == input_device_name:
                input_device_index = dev['index']
                break

        print(f"Using: {input_device_name} at index {input_device_index}")

        self.stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            input=True,
            frames_per_buffer=self.buffer_size,
            input_device_index=input_device_index)

        print("Stream opened")

    def listen(self, on_awaken=None, on_transcription=None):

        while True:
            mic_data = self.stream.read(self.buffer_size, exception_on_overflow=False)

            if self.auto_listen:
                if self.audio.mixer.music.get_busy():
                    continue
                else:
                    self.auto_listen = False
                    self.start_listening()

            if self.rec.AcceptWaveform(mic_data):

                result = self.rec.Result()
                result_dict = json.loads(result)
                text = result_dict.get('text', '').strip()

                if on_awaken:
                    if self.prefix in text.lower():
                        on_awaken(self, text)
                        continue

                if on_transcription:
                    on_transcription(self, text)
                    continue

    def listen_again(self):
        self.auto_listen = True

    def stop_listening(self):
        self.listening = False

    def start_listening(self):
        self.listening = True
        print("Listening...")
        self.audio.play("bin/audio/listening.mp3")

    def __del__(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.mixer.quit()
        print("Audio stream closed")