"""Handles interfacing with Spotify"""
import pprint
import spotipy
import spotipy.util as util

import sys

sys.path.append('..')
from common.core import *
from common.gfxutil import *
from common.audio import *
from common.mixer import *
from common.note import *
from common.wavegen import *
from common.wavesrc import *

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Rectangle

import random

# harded coded values for spotify app
client_id = 'f443660f40d348caa7b717a385341278'
client_secret = '545a451afb794c2f83feb68547182da1'
scope = 'user-read-currently-playing, user-read-playback-state'

CONFIDENCE_THRESHOLD = 0.01


class Song:
    """Runs audio analysis on given song"""

    def __init__(self, spotify, track, duration):
        self.track = track
        self.sp = spotify
        self.duration = duration
        self.beats = []
        self.sections = []

        self.bars = []

        data = self.sp.audio_analysis(self.track)

        # sort through beats, eliminate under-confident beats
        for b in data['beats']:
            if b['confidence'] > CONFIDENCE_THRESHOLD:
                self.beats.append((b['start'], b['duration']))

        for s in data['sections']:
            # sections threshold must be 0 for progress bar to render correctly

            if s['confidence'] > 0:
                self.sections.append((s['start'], s['duration']))

        for b in data['bars']:
            if b['confidence'] > CONFIDENCE_THRESHOLD:
                self.bars.append((b['start'], b['duration']))

        # print('loaded song')

        print(data['bars'])

    def get_sections(self):
        return self.sections

    def get_beats(self):
        return self.beats

    def on_beat(self, time, threshold):
        """
        :param time: Current time in ms
        :param threshold: Slop window threshold (in ms)
        :return: True if on a beat timestamp within threshold, False otherwise
        """
        i = 0
        time /= 1000  # to milliseconds
        for i in range(len(self.beats)):
            if self.beats[i][0] > time:
                break

        # return True is close enough to beat directly before or after
        return abs(time - self.beats[i - 1][0]) < threshold or abs(time - self.beats[i][0]) < threshold

    def on_bar(self, time, threshold):
        """
        :param time: Current time in ms
        :param threshold: Slop window threshold in ms
        :return: True if on a bar timestamp within threshold, False otherwise
        """
        i = 0
        time = time / 1000
        for i in range(len(self.bars)):
            if self.bars[i][0] > time:
                break

        # return true is close enough to beat directly before or after
        return abs(time - self.bars[i - 1][0]) < threshold or abs(time - self.bars[i][0]) < threshold


class User:
    """Represents data about current user and user playback."""

    def __init__(self, username):
        self.username = username

        # unique token for each account
        self.token = util.prompt_for_user_token(self.username, scope, client_id=client_id, client_secret=client_secret,
                                                redirect_uri="https://www.spotify.com/us/")

        self.sp = spotipy.Spotify(auth=self.token)

        self.current_track = None
        self.current_playback_data = self.sp.current_playback()

        self.artists = []
        self.song_name = ""

        if self.current_playback_data:
            # make song object for song currently playing
            # for now, switching songs will not update the beats so use one song while testing
            self.current_track = Song(self.sp, self.current_playback_data['item']['id'],
                                      self.current_playback_data['item']['duration_ms'])
            self.song_name = self.current_playback_data['item']['name']
            for artist in self.current_playback_data['item']['artists']:
            	self.artists.append(artist['name'])
    def get_song_name(self):
    	return self.song_name

    def get_artists(self):
    	return self.artists
    	
    def get_spotify(self):
        return self.sp

    def get_token(self):
        return self.token

    def get_current_track(self):
        return self.current_track

    def get_time(self):
        # get progress_ms
        playback = self.sp.current_playback()
        if playback:
            return playback['progress_ms']

    def get_progress(self):
        # get fraction of song that has played
        progress = self.get_time()
        if progress:
            return progress / self.current_track.duration
        else:
            return 0

    def is_playing(self):
        """

        :return: True if a song is playing, False if not (e.g. paused song)
        """
        if self.sp.current_playback() is None:
            return False
        else:
            return True


class ProgressBarTest(InstructionGroup):
    """Graphics representing progress bar. Animates the fraction of the song that has played"""

    def __init__(self, sections, duration):
        super(ProgressBar, self).__init__()

        self.add(Color(rgb=(0.2, 0.8, 0.5)))
        self.length = Window.width * 0.9
        self.buffer = Window.width * 0.05

        self.sections = sections
        self.duration = duration

        start_pos = self.buffer
        for section in self.sections:
            self.add(Color(rgb=(0.2, random.random(), 0.5)))

            section_length = section[1] * 1000
            bar_length = self.length * (section_length / self.duration)
            bar = Rectangle(pos=(start_pos, self.buffer), size=(bar_length, self.buffer))
            start_pos += bar_length
            self.add(bar)

        self.add(Color(rgb=(0.4, 0.1, 0.1)))
        self.progress_mark = Rectangle(pos=(self.buffer, self.buffer), size=(self.buffer / 10, self.buffer))
        self.add(self.progress_mark)

    def on_update(self, progress):
        self.progress_mark.pos = ((self.length * progress) + self.buffer, self.buffer)


class TestWidget(BaseWidget):
    def __init__(self):
        super(TestWidget, self).__init__()

        # Serena's account
        self.user = User('1235254187')
        # self.user = User('isabelkaspriskie')
        # will only work for initial song
        self.sections = self.user.get_current_track().get_sections()
        self.duration = self.user.get_current_track().duration

        self.bar = ProgressBarTest(self.sections, self.duration)
        self.canvas.add(self.bar)

    def on_key_down(self, keycode, modifiers):

        # test on_beat function
        if keycode[1] == 'a':
            song = self.user.get_current_track()
            time = self.user.get_time()
            print(time, song.on_beat(time, 0.2))

    def on_update(self):
        progress = self.user.get_progress()

        self.bar.on_update(progress)

        song = self.user.get_current_track()
        time = self.user.get_time()
        if song.on_bar(time, 0.1):
            print("bar", time)


if __name__ == '__main__':
    run(TestWidget)
