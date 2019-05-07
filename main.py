import sys
sys.path.append('..')

from graphics import *
from spotify import *
import threading
import time

# https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-analysis/#timbre


global song_time
song_time = 0

global is_playing
is_playing = False

global song_name
song_name = ""

class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        self.audio = Audio('1235254187')  # Serena
        # self.audio = Audio("isabelkaspriskie")  # Isabel
        # self.audio = Audio("shann0nduffy")  # Shannon

        self.background = AmbientBackgroundCircles(alpha=0.4, num_circles=20)
        self.canvas.add(self.background)

        self.sections = self.audio.get_current_track().get_sections_data()
        self.duration = self.audio.get_current_track().duration

        self.progress_bar = ProgressBar(self.sections, self.duration)
        self.canvas.add(self.progress_bar)

        self.ui = User(self.audio, self.progress_bar)
        self.canvas.add(self.ui)

        self.is_up = False
        self.is_down = False
        self.spacebar_down = False

        # Static text display
        self.info = topleft_label(font_filepath="res/font/CabinCondensed-Regular.ttf")
        self.add_widget(self.info)

        self.song_info = song_label()
        self.add_widget(self.song_info)

        # seems to be some lag??
        #self.time = self.audio.get_time() / 1000 # Song position in ms
        self.time = song_time
        #self.time = self.audio.get_time() 
        self.progress = 0  # Song position in percent completion
        self.spotify_playing = self.audio.is_playing()  # Flag on whether Spotify is playing a song or not
        self.name = self.audio.song_name

        # THREADING
        self.api_thread = threading.Thread(target=self.call_api, args = (), daemon=True)
        self.api_thread.start()
        
    def on_key_down(self, keycode, modifiers):
        if keycode[1] == 'spacebar':
            self.ui.spacebar()

    def on_touch_move(self, touch):
        self.ui.on_touch_move(touch)

    def call_api(self):
        # continuously call spotify api to update time
        # returns playing flag and time
        global song_time
        global is_playing
        global song_name
        while True:
            if self.audio.get_time() != None:
                song_time = self.audio.get_time()
                is_playing = self.audio.is_playing()
                song_name = self.audio.get_song_name()

    def on_update(self):
        global song_time
        global is_playing
        global song_name

        
        # use spotify time if updated, else use kivyClock
        if self.time < song_time:
            self.time = song_time
        elif is_playing:
            self.time += kivyClock.frametime * 1000

        self.progress = song_time / self.audio.current_track.duration
        fps = kivyClock.get_fps()

        # if self.audio.is_playing():
        #self.time += kivyClock.frametime * 1000
        #self.time = song_time

        if self.time > self.duration or song_name != self.name:
            self.audio.update_song()
            self.time = self.audio.get_time()
            self.progress = self.time / self.audio.current_track.duration

            self.sections = self.audio.get_current_track().get_sections_data()


            self.duration = self.audio.get_current_track().duration
            self.canvas.remove(self.progress_bar)

            self.progress_bar = ProgressBar(self.sections, self.duration)
            self.ui.update_progress_bar(self.progress_bar)


            self.canvas.add(self.progress_bar)

            self.name = song_name
            #self.progress_bar.update_song(self.sections, self.duration)

            self.time = song_time

        self.info.text = ''
        self.info.text += 'time: %.2f\n' % self.time
        self.info.text += 'fps: %.2f\n' % fps
        self.info.text += 'progress: %.2f \n' % self.progress

        self.song_info.text = self.name + '\n'
        self.song_info.text +=  str(self.audio.artists) + '\n'

        self.ui.on_update(self.time)
        self.background.on_update(self.time)
        self.progress_bar.on_update(self.progress)

        # print(self.audio.get_current_track().get_section_index(self.time))

def song_label(font_filepath='res/font/CabinCondensed-Regular.ttf', font_size='20sp'):
    l = Label(text = "text", valign='top', halign='right', font_size=font_size,
              pos = ( 0.80 * Window.width, Window.height * 0.4 ),
              text_size=( 0.25 * Window.width, Window.height))
    # print(l.pos)
    if font_filepath is not None:
        l.font_name = font_filepath
    return l


if __name__ == "__main__":
    run(MainWidget)
