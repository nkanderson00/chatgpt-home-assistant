from libs import gpt

volume_prompt = """
You are in control of the volume and pause/play button of a speaker playing music. 
You will be given a message to respond to.
If I say something related to sound or volume level, respond with "command volume X.XX" where X.XX is a number between 0 and 1.
If I say something related to pausing or resuming, respond with "command pause" or "command resume".
If you are not completely sure of the intention, respond with "no command".
The volume is currently {vol}. Respond to: "{text}"
"""

class VolumeControl:

    def __init__(self, audio, volume=1.0):
        self.audio = audio
        self.mixer = audio.mixer
        self.volume = volume
        self.listening = False

    def get_command(self, text):
        volume_ai = gpt.get_gpt("gpt-3.5-turbo")
        volume_response = volume_ai.ask(volume_prompt.format(vol=self.volume, text=text))
        volume_response = volume_response.strip(".")
        volume_response = volume_response.strip("\"")

        print("Volume AI: " + volume_response)

        if volume_response.lower().startswith("command") and len(volume_response.split(" ")) <= 3:
            if "pause" in volume_response:
                self.mixer.music.pause()
                self.audio.speak("Music paused")
            elif "resume" in volume_response:
                if self.audio.music_stream:
                    self.audio.music_stream.resume()
            elif "volume" in volume_response:
                self.volume = float(volume_response.split(" ")[-1])
                if 0 <= self.volume <= 1:
                    self.mixer.music.set_volume(self.volume)
                    if self.audio.music_stream:
                        self.audio.music_stream.set_volume(self.volume)
                        self.audio.music_stream.resume()
                    self.audio.play("bin/audio/listening.mp3")
                    print("Volume set to " + str(self.volume))

            return True

        else:
            return False

    def get_volume(self):
        return self.volume