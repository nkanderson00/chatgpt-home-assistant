import threading
import time
import yt_dlp
import vlc
from youtubesearchpython import VideosSearch

class AudioStream:
    def __init__(self, query):
        self.query = query
        videos = VideosSearch(query, limit=30)
        self.url = None
        self.video_title = None
        for video in videos.result()['result']:
            if video['duration'] is not None and video["viewCount"]["text"] is not None:
                self.url = video['link']
                self.video_title = video['title']
                break
        self.player = None
        self.playing = False
        self.paused = False
        self.volume = None
        self.thread = threading.Thread(target=self.run)

    def start(self):
        self.thread.start()

    def stop(self):
        self.playing = False

    def pause(self):
        if not self.paused:
            self.paused = True
            self.player.pause()

    def resume(self):
        self.paused = False
        self.player.play()

    def set_volume(self, volume):
        self.volume = int(volume*100)
        if self.player:
            self.player.audio_set_volume(self.volume)

    def run(self):
        # Set stream options
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'forceurl': True,
        }

        # Extract the direct URL of the best audio stream
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(self.url, download=False)
            audio_url = result['url']

        # Create a VLC media player object and start playing the audio stream
        vlc_instance = vlc.Instance()
        self.player = vlc_instance.media_player_new()
        media = vlc_instance.media_new(audio_url)
        self.player.set_media(media)
        self.player.audio_set_volume(self.volume)
        self.player.play()
        self.playing = True

        # Wait for the player to finish playing the audio stream or for stop command
        while True:
            if self.playing:
                state = self.player.get_state()
                if state == vlc.State.Ended:
                    self.playing = False
            else:
                break
            time.sleep(0.1)



if __name__ == "__main__":

    # Create an AudioStream object and start the audio stream and input thread
    stream = AudioStream("lo fi hip hop")

    #exit()

    stream.start()
    #stream.start_input_thread()


    time.sleep(8)
    print("Pausing...")
    stream.pause()
    time.sleep(3)
    print("Resuming...")
    stream.resume()
    time.sleep(3)
    print("Stopping...")
    stream.stop()

    # Stop the audio stream and join the thread
    stream.stop()
    stream.thread.join()