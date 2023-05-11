import speech_recognition as sr
import requests
import pyaudio

class Recognizer:

    def __init__(self,
                 audio,
                 model_path="",
                 input_device_name="Blue Snowball: USB Audio (hw:1,0)",
                 sample_rate=16000,
                 prefix="computer"):

        self.audio = audio
        self.buffer_size = 4096
        self.sample_rate = sample_rate
        self.prefix = prefix
        self.listening = False
        self.auto_listening = None
        self.gpt_models = ("text-curie-001", "gpt-3.5-turbo")
        self.gpt_model = 0
        self.transcriber_url = "http://192.168.1.33:2023/transcribe"
        p = pyaudio.PyAudio()

        self.input_device_index = 0
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev['name'] == input_device_name:
                self.input_device_index = dev['index']
                break

        print(f"Using: {input_device_name} at index {self.input_device_index}")

    def listen(self, on_awaken=None, on_transcription=None):

        r = sr.Recognizer()
        r.energy_threshold = 10
        r.pause_threshold = 0.8
        r.dynamic_energy_threshold = True

        with sr.Microphone(sample_rate=self.sample_rate, device_index=self.input_device_index) as source:
            r.adjust_for_ambient_noise(source)

            while True:

                if self.auto_listening:
                    if self.audio.mixer.music.get_busy():
                        continue
                    else:
                        self.auto_listening = False
                        self.start_listening()

                if not self.listening:
                    print("Listening for wakeup")
                    audio = r.listen(source, phrase_time_limit=2)
                else:
                    print("Listening for speech")
                    audio = r.listen(source, phrase_time_limit=10)

                audio_data = audio.get_raw_data()

                try:
                    response = requests.post(self.transcriber_url, data=audio_data, timeout=10)
                    result = response.json()
                    text = result["text"].strip().lower()
                except requests.exceptions.Timeout:
                    text = "Could not connect to the server in time."
                except requests.exceptions.ConnectionError:
                    text = "Could not connect to the server."
                except requests.exceptions.RequestException as e:
                    text = f"Could not connect to the server: {e}"
                except Exception as e:
                    text = f"Error: {e}"

                if not text:
                    continue

                if not self.listening:
                    if on_awaken:
                        if self.prefix in text.lower():
                            self.start_listening()
                            on_awaken(text)
                            continue
                else:
                    if on_transcription:
                        on_transcription(text)
                        self.stop_listening()
                        continue

    def stop_listening(self):
        self.listening = False
        print("Stopped listening")

    def start_listening(self):
        self.listening = True
        self.audio.play("bin/audio/listening.mp3")

    def start_auto_listen(self):
        self.auto_listening = True
        print("Auto listening enabled")

    def __del__(self):
        self.audio.mixer.quit()
        print("Audio stream closed")