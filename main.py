import sys
sys.path.append('..')

from graphics import *
from spotify import *

# https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-analysis/#timbre


class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        #self.audio = Audio('1235254187')  # Serena
        # self.audio = User("isabelkaspriskie")  # Isabel
        self.audio = Audio("shann0nduffy")  # Shannon

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
        self.info = topleft_label()
        self.add_widget(self.info)


        # seems to be some lag??
        #self.time = self.audio.get_time() - 1500 # Song position in ms

        self.time = self.audio.get_time() 
        self.progress = 0  # Song position in percent completion
        self.spotify_playing = self.audio.is_playing()  # Flag on whether Spotify is playing a song or not

    def on_key_down(self, keycode, modifiers):
        # up/down key will move character
        # spacebar will release bubbles
        if keycode[1] == 'up':
            self.is_up = True

        if keycode[1] == 'down':
            self.is_down = True

        if keycode[1] == 'spacebar':
            self.spacebar_down = True

    def on_key_up(self, keycode):
        # spacebar: stop releasing bubbles
        # up/down: stop moving
        if keycode[1] == 'up':
            self.is_up = False

        if keycode[1] == 'down':
            self.is_down = False

        if keycode[1] == 'spacebar':
            self.spacebar_down = False

    def on_update(self):
        self.progress = self.time / self.audio.current_track.duration
        fps = kivyClock.get_fps()

        # if self.audio.is_playing():
        self.time += kivyClock.frametime * 1000

        if self.time > self.duration:
            self.audio.update_song()
            self.time = self.audio.get_time()
            self.progress = self.time / self.audio.current_track.duration


            self.sections = self.audio.get_current_track().get_sections_data()
            self.duration = self.audio.get_current_track().duration
            self.progress_bar.update_song(self.sections, self.duration)


        self.info.text = ''
        self.info.text += 'time: %.2f\n' % self.time
        self.info.text += 'fps: %.2f\n' % fps
        self.info.text += 'progress: %.2f \n' % self.progress
        self.info.text += 'song name: ' + self.audio.get_song_name() + '\n'
        self.info.text += 'artists: ' + str(self.audio.get_artists()) + '\n'

        self.ui.on_update(self.time)

        self.progress_bar.on_update(self.progress)

        # print(self.audio.get_current_track().get_section_index(self.time))


if __name__ == "__main__":
    run(MainWidget)
