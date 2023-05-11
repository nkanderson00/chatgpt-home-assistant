import traceback
from libs import gpt, audio
from libs import stt_whisper as stt

def clean_text(text: str):
    """
    Removes "Me:" and "You:" from the beginning of each line
    """
    lines = text.split("\n")
    cleaned_lines = [line[3:] if line.startswith("Me:") else line[4:] if line.startswith("You:") else line for line in lines]
    return " ".join(cleaned_lines)


class Assistant:

    def __init__(self):
        self.ai = gpt.get_gpt()
        self.aud = audio.Audio()
        self.recognizer = stt.Recognizer(self.aud, model_path="bin/vosk-model-small-en-us-0.15")

    def on_awaken(self, text):
        if self.aud.music_stream:
            self.aud.music_stream.pause()

    def on_transcription(self, text):
        print("Heard: " + text)

        if text.lower() in ("change mode", "switch mode"):
            model = int(not self.recognizer.gpt_model)
            self.ai = gpt.get_gpt(self.recognizer.gpt_models[model])
            print("Mode changed to " + self.recognizer.gpt_models[model])
            self.aud.speak("Mode changed to " + self.recognizer.gpt_models[model])
            return

        elif text.lower().startswith("play"):
            music_query = text[5:]
            self.aud.play("bin/audio/loading_music.mp3")

            try:
                self.aud.play_music(music_query)
            except Exception as e:
                traceback.print_exc()
                self.aud.speak("Sorry, an error occurred: " + str(e))
            finally:
                return

        if self.aud.volume_control.get_command(text):
            return

        print("Human: " + text)

        if self.recognizer.gpt_models[self.recognizer.gpt_model] == "gpt-3.5-turbo":
            self.aud.speak("Let me think about that...")

        ai_response = clean_text(self.ai.ask(text))
        print("AI: " + ai_response)

        if ai_response:
            if ai_response.endswith("?"):
                self.recognizer.start_auto_listen()
            self.aud.speak(ai_response)


    def run(self):
        self.recognizer.listen(on_awaken=self.on_awaken, on_transcription=self.on_transcription)



if __name__ == "__main__":
    Assistant().run()