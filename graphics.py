import sys
sys.path.append('..')
from common.core import *
from common.gfxutil import *
from common.audio import *
from common.mixer import *
from common.note import *
from common.wavegen import *
from common.wavesrc import *

from kivy.core.window import Window, WindowBase
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate

from random import random, choice

from spotify import Song, User

# Constants
kSpeed = 5000  # pixels/sec
kPalette = {'red400': (0.9372549019607843, 0.3254901960784314, 0.3137254901960784),
            'pink400': (0.9254901960784314, 0.25098039215686274, 0.47843137254901963),
            'purple400': (0.6705882352941176, 0.2784313725490196, 0.7372549019607844),
            'deep_purple400': (0.49411764705882355, 0.3411764705882353, 0.7607843137254902),
            'indigo400': (0.3607843137254902, 0.4196078431372549, 0.7529411764705882),
            'blue400': (0.25882352941176473, 0.6470588235294118, 0.9607843137254902),
            'light_blue400': (0.1607843137254902, 0.7137254901960784, 0.9647058823529412),
            'cyan400': (0.14901960784313725, 0.7764705882352941, 0.8549019607843137),
            'teal400': (0.14901960784313725, 0.6509803921568628, 0.6039215686274509),
            'green400': (0.4, 0.7333333333333333, 0.41568627450980394),
            'light_green400': (0.611764705882353, 0.8, 0.396078431372549),
            'lime400': (0.8313725490196079, 0.8823529411764706, 0.3411764705882353),
            'yellow400': (1.0, 0.9333333333333333, 0.34509803921568627),
            'amber400': (1.0, 0.792156862745098, 0.1568627450980392),
            'orange400': (1.0, 0.6549019607843137, 0.14901960784313725),
            'deep_orange400': (1.0, 0.4392156862745098, 0.2627450980392157),
            'brown400': (0.5529411764705883, 0.43137254901960786, 0.38823529411764707),
            'blue_gray400': (0.47058823529411764, 0.5647058823529412, 0.611764705882353),
            'gray50': (0.9803921568627451, 0.9803921568627451, 0.9803921568627451),
            'gray400': (0.7411764705882353, 0.7411764705882353, 0.7411764705882353),
            'gray800': (0.25882352941176473, 0.25882352941176473, 0.25882352941176473),
            'gray900': (0.12941176470588237, 0.12941176470588237, 0.12941176470588237),
            }


class ProgressBar(InstructionGroup):
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


class Character(InstructionGroup):
    """Character draws the character, handles audio data, and draws bubbles behind the character"""
    def __init__(self, spotify_song=None):
        super().__init__()

        self.audio = spotify_song

        self.character = CEllipse(cpos=(Window.width*3/4, Window.height/2), csize=(50, 50), sizesegments=20)
        self.color = Color(*kPalette["gray50"])
        self.add(self.color)
        self.add(self.character)

        self.onbeat_bubbles = set()
        self.offbeat_bubbles = set()
        self.kill_list = set()

        self.is_onbeat = False
        self.last_beat = 0
        # count the number of iterations that have been on beat
        self.num_beats = 0

        # Time keeping
        # self.duration = duration
        # self.speed = speed
        self.time = 0
        self.on_update(0)

    def get_num_objects(self):
        return len(self.onbeat_bubbles + self.offbeat_bubbles)

    def spacebar(self, time):
        self.time = time
        if self.is_onbeat and self.num_beats == 1:
            bubble = OnBeatBubble(self.character.cpos, 20, kPalette["teal400"], kSpeed)
            self.add(bubble)
            self.onbeat_bubbles.add(bubble)
        else:
            bubble = OffBeatSpray((self.character.cpos[0]/2, self.character.cpos[1]/2),
                                  [kPalette["yellow400"], kPalette["purple400"]],
                                  animate=False)
            self.add(bubble)
            self.offbeat_bubbles.add(bubble)

    def on_up_press(self):
        current_pos = self.character.cpos
        if current_pos[1] < Window.height:
            self.character.cpos = (current_pos[0], current_pos[1] + 10)

    def on_down_press(self):
        current_pos = self.character.cpos
        if current_pos[1] > 0:
            self.character.cpos = (current_pos[0], current_pos[1] - 10)

    def on_update(self, time):
        self.time = time

        #if self.audio.is_onbeat():
        for bubble in self.kill_list:
            if bubble in self.onbeat_bubbles:
                self.onbeat_bubbles.remove(bubble)
            elif bubble in self.offbeat_bubbles:
                self.offbeat_bubbles.remove(bubble)
            self.remove(bubble)
            self.kill_list.remove(bubble)

        self.is_onbeat = self.audio.get_current_track().on_beat(self.time, 0.1)

        if self.is_onbeat:
            self.num_beats += 1
        else:
            self.num_beats = 0

        if self.is_onbeat:
            for bubble in self.onbeat_bubbles:
                bubble.on_beat()

        for bubble in self.onbeat_bubbles | self.offbeat_bubbles:
            bubble.on_update(self.time)

        for bubble in self.onbeat_bubbles:
            if bubble.dot.cpos[0] < -20 and bubble not in self.onbeat_bubbles:
                self.kill_list.add(bubble)

        for bubble in self.offbeat_bubbles:
            if bubble.translate.x < -Window.width/2 and bubble not in self.offbeat_bubbles:
                self.kill_list.add(bubble)


class OnBeatBubble(InstructionGroup):
    def __init__(self, pos, radius, color, speed):
        super().__init__()

        self.original_pos = pos
        self.radius = radius

        # Color
        self.color = Color(*color)
        self.add(self.color)

        # Shape
        self.dot = CEllipse(cpos=pos, csize=(2 * radius, 2 * radius), sizesegments=20)
        self.add(self.dot)

        # Animation
        self.beat_anim = None
        self.pos_anim = KFAnim((0, pos[0]), (speed/pos[0], 0))
        self.shrink = False

        # Time keeping
        self.time = 0
        self.on_update(0)

    def on_beat(self):
        self.beat_anim = KFAnim((self.time, self.radius), (self.time+0.1, 2*self.radius))

    def on_update(self, time):
        # rad = self.radius_anim.eval(self.time)
        # self.dot.csize = 2*rad, 2*rad

        self.dot.cpos = (self.dot.cpos[0] - 10, self.dot.cpos[1])

        if self.beat_anim is not None:
            radius = self.beat_anim.eval(self.time)
            self.dot.csize = (2*radius, 2*radius)
            if radius == 2*self.radius:
                self.beat_anim = KFAnim((self.time, 2*self.radius), (self.time+0.1, self.radius))
                self.shrink = True
            if radius == self.radius and self.shrink:
                self.beat_anim = None
                self.shrink = False

        self.time = time
        # return self.radius_anim.is_active(self.time)


class OffBeatSpray(InstructionGroup):
    def __init__(self, pos, colors, bound=30, dot_size=5, num_dots=10, animate=False):
        """
        If the player hits the spacebar off the beat, a spray of dots will be placed onscreen.
        The colors map to the two most prominent pitch classes of that beat.

        :param pos: (tuple) center position of spray in pixels, e.g. (1040, 980)
        :param colors: (tuple) possible tuples for the color, e.g. ((255, 255, 255), (155, 155, 251))
        :param bound: (int) radial bound on the spray
        :param dot_size: (int) radius of the dots
        :param num_dots: (int) number of dots in the spray
        :param animate: (boolean) True if the dots will move around within the bound, False otherwise
        """
        super().__init__()
        self.pos = np.array(pos)
        self.colors = colors
        self.bound = bound
        self.rad = dot_size
        self.num_dots = num_dots
        self.animate = animate

        # Time keeping for animation?
        self.time = 0

        # The entire spray should be able to move as one object
        self.add(PushMatrix())
        self.translate = Translate(*pos)
        self.add(self.translate)

        # For each dot in the spray, pick a random x, y coordinates using random radius, theta in ranges
        # [0, self.bound], [0, 2pi] respectively
        #       x = x_0 + r * cos(theta)
        #       y = y_0 + r * sin(theta)
        self.dots = [CEllipse(cpos=(self.pos[0] + self.bound * random() * np.cos(2 * np.pi * random()),
                                    self.pos[1] + self.bound * random() * np.sin(2 * np.pi * random())),
                              size=(self.rad, self.rad), segments=4) for i in range(self.num_dots)]

        for dot in self.dots:
            self.add(Color(*choice(self.colors)))
            self.add(dot)

        self.add(PopMatrix())

    def on_update(self, time):
        self.time = time
        if self.animate:
            for dot in self.dots:
                dot.pos = (dot.pos[0] + choice((-1, 1)) * random() * 2,
                           dot.pos[1] + choice((-1, 1)) * random() * 2)
        self.translate.x = self.translate.x - 10


class TestWidget(BaseWidget):
    def __init__(self):
        super().__init__()

        self.spray = OffBeatSpray((300, 300), ((100, 0, 30), (0, 50, 200)), animate=False)
        self.canvas.add(self.spray)

        self.one_bubble = OnBeatBubble((Window.width * 3 / 4, Window.height / 2), 20, (1, 1, 0), 10000)
        self.canvas.add(self.one_bubble)

        self.time = 0

    def on_update(self, time):

        if self.time > 2:
            self.one_bubble.on_beat()
            self.time -= 2

        self.spray.on_update()

        self.one_bubble.on_update(time)

        self.time = time


if __name__ == "__main__":
    run(TestWidget)