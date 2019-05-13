import sys
import threading
sys.path.append('..')

from common.core import *
from common.gfxutil import *

from kivy.graphics.instructions import InstructionGroup

from random import random, choice, shuffle

from graphics.background import AmbientBackgroundBlobs
from graphics.modes.kaleidoscope import Kaleidoscope
from graphics.modes.pulsing_bar import PulsingBar
from graphics.modes.prism import Prism
from graphics.modes.spectral_bars import SpectralBars
from graphics.modes.tunnel import Tunnel
from graphics.mode_transition import ModeTransition
from graphics.progress_bar import ProgressBar
from spotify import *


global song_time
song_time = 0

global is_playing
is_playing = False

global song_name
song_name = ""

global artist_names
artist_names = ""

global album_name
album_name = ""

# https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-analysis/#timbre


class User(InstructionGroup):
    """ The User handles the audio analysis data and can call methods on the visualizer modes. """

    def __init__(self, spotify_song, progress_bar):
        super().__init__()

        self.audio = spotify_song
        self.progress_bar = progress_bar

        num_sections = len(self.audio.get_current_track().get_sections())

        # list of all background "shape" categories
        self.backgrounds = ["a", "b", "c", "d"]

        # the background for each section is random
        self.section_backgrounds = [int(random() * len(self.backgrounds)) for _ in range(num_sections)]

        # instance of current background
        self.current_background = None

        # list of all modes
        self.modes = [PulsingBar, Tunnel, SpectralBars, Prism, Kaleidoscope]

        # the mode for each section
        self.section_modes = [int(random() * len(self.modes)) for i in
                              range(len(self.audio.get_current_track().get_sections()))]

        # instance of current mode
        self.current_mode = None

        self.is_onbeat = False
        self.last_beat = 0

        self.in_transition = False
        self.transition_time = 1000  # ms

        # count the number of iterations that have been on beat
        self.num_beats = 0

        self.current_segment = 0
        self.current_section = -1

        # Time keeping
        self.time = 0
        self.on_update(0)

        self.play = True

    def play(self):
        self.play = True

    def pause(self):
        self.play = False

    def spacebar(self):
        if self.play:
            self.play = False
        else:
            self.play = True

    def update_progress_bar(self, progress_bar):
        self.progress_bar = progress_bar

    def on_bar(self):
        if self.current_mode:
            self.current_mode.on_bar(touch)

    def on_update(self, time):
        self.time = time

        self.is_onbeat = self.audio.get_current_track().on_beat(self.time, 0.1)

        self.is_onbar = self.audio.get_current_track().on_bar(self.time, 0.1)

        section_index = self.audio.get_current_track().get_section_index(time)

        if section_index == -1:
            return

        time_to_next = self.audio.get_current_track().get_time_to_next_section(time)
        color = self.progress_bar.get_section_color(section_index)
        if time_to_next < self.transition_time / 1000 and not self.in_transition and time_to_next != -1:
            self.in_transition = True

            new_background = AmbientBackgroundBlobs(shape=choice(self.backgrounds))
            if self.current_background:
                self.remove(self.current_background)
            self.add(new_background)

            self.current_background = new_background

            color = self.progress_bar.get_section_color(section_index + 1)
            shuffle(self.modes)
            new_mode = ModeTransition(color, self.modes[0], self.modes[1], self.time, self.transition_time)

            if self.current_mode:
                self.remove(self.current_mode)
            self.add(new_mode)

            self.current_mode = new_mode
            self.current_section = section_index + 1


        elif section_index != self.current_section and not self.in_transition and section_index != -1:
            self.in_transition = True

            new_background = AmbientBackgroundBlobs(shape=choice(self.backgrounds))
            if self.current_background:
                self.remove(self.current_background)
            self.add(new_background)

            self.current_background = new_background

            color = self.progress_bar.get_section_color(section_index)
            shuffle(self.modes)
            new_mode = ModeTransition(color, self.modes[0], self.modes[1], self.time, self.transition_time)

            if self.current_mode:
                self.remove(self.current_mode)
            self.add(new_mode)

            self.current_mode = new_mode
            self.current_section = section_index



        self.in_transition = self.current_mode.in_transition(self.time, self.transition_time)

        # if section_index != self.current_section:
        #     # new section
        #     # print(section_index)
        #     new_mode = self.modes[self.section_modes[section_index]](self.progress_bar.get_section_color(section_index))
        #     if self.current_mode:
        #         self.remove(self.current_mode)
        #     self.add(new_mode)

        #     self.current_mode = new_mode
        #     self.current_section = section_index

        if self.is_onbeat:
            self.num_beats += 1
        else:
            self.num_beats = 0

        if self.is_onbeat:
            self.current_mode.on_beat()

        if self.is_onbar:
            self.current_mode.on_bar()

        segment_index = self.audio.get_current_track().get_segment_index(time)
        if segment_index != self.current_segment:
            self.current_segment = segment_index
            data = self.audio.get_current_track().get_segments_data()[self.current_segment]
            self.current_mode.on_segment(data)
            self.progress_bar.pitch_pulse.on_segment(data, color)

        self.current_mode.on_update(self.time)
        self.current_background.on_update(self.time)


class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        # self.audio = Audio('1235254187')  # Serena
        self.audio = Audio("isabelkaspriskie")  # Isabel
        # self.audio = Audio("shann0nduffy")  # Shannon

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
        self.right_info = song_label()
        self.add_widget(self.right_info)

        self.left_info = left_label()
        self.add_widget(self.left_info)

        # seems to be some lag??
        #self.time = self.audio.get_time() / 1000 # Song position in ms
        self.time = song_time
        #self.time = self.audio.get_time() 
        self.progress = 0  # Song position in percent completion
        self.spotify_playing = self.audio.is_playing()  # Flag on whether Spotify is playing a song or not
        self.name = self.audio.song_name
        self.album_name = self.audio.album_name
        self.artists = ", ".join(self.audio.artists)

        # THREADING
        self.api_thread = threading.Thread(target=self.call_api, args = (), daemon=True)
        self.api_thread.start()
        
    def on_key_down(self, keycode, modifiers):
        if keycode[1] == 'spacebar':
            self.ui.spacebar()

    def call_api(self):
        # continuously call spotify api to update time
        # returns playing flag and time
        global song_time
        global is_playing
        global song_name
        global album_name
        global artist_names
        while True:
            if self.audio.get_time() != None:
                song_time = self.audio.get_time()
                is_playing = self.audio.is_playing()
                song_name = self.audio.get_song_name()
                album_name = self.audio.get_album()
                artist_names = ", ".join(self.audio.get_artists())

    def on_update(self):
        global song_time
        global is_playing
        global song_name
        global album_name
        global artist_names

        
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
            self.album_name = album_name
            self.artists = artist_names
            #self.progress_bar.update_song(self.sections, self.duration)

            self.time = song_time


        self.left_info.text = self.name + '\n'
        self.right_info.text = self.artists + '\n'
        # self.right_info.text += self.album_name + '\n'

        self.ui.on_update(self.time)
        self.progress_bar.on_update(self.progress)

        # print(self.audio.get_current_track().get_section_index(self.time))


def left_label(font_filepath='res/font/CabinCondensed-Regular.ttf', font_size='20sp'):
    l = Label(text="text", valign='top', halign='left', font_size=font_size,
              pos=(0.15 * Window.width, Window.height * 0.4),
              text_size=(0.25 * Window.width, Window.height))
    # print(l.pos)
    if font_filepath is not None:
        l.font_name = font_filepath
    return l


def song_label(font_filepath='res/font/CabinCondensed-Regular.ttf', font_size='20sp'):
    l = Label(text="text", valign='top', halign='right', font_size=font_size,
              pos=(Window.width * 0.8, Window.height * 0.4),
              text_size=(0.25 * Window.width, Window.height))
    if font_filepath is not None:
        l.font_name = font_filepath
    return l

if __name__ == "__main__":
    run(MainWidget)
