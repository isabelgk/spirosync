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

kSpeed = 10000  # pixels/sec

# MaterialUI color palette (rgb)
kPalette = {"red400": (239, 83, 80),
            "pink400": (236, 64, 122),
            "purple400": (171, 71, 188),
            "deep_purple400": (126, 87, 194),
            "indigo400": (92, 107, 192),
            "blue400": (66, 165, 245),
            "light_blue400": (41, 182, 246),
            "cyan400": (38, 198, 218),
            "teal400": (38, 166, 154),
            "green400": (102, 187, 106),
            "light_green400": (156, 204, 101),
            "lime400": (212, 225, 87),
            "yellow400": (255, 238, 88),
            "amber400": (255, 202, 40),
            "orange400": (255, 167, 38),
            "deep_orange400": (255, 112, 67),
            "brown400": (141, 110, 99),
            "blue_gray400": (120, 144, 156),
            "gray50": (250, 250, 250),
            "gray400": (189, 189, 189),
            "gray800": (66, 66, 66),
            "gray900": (33, 33, 33),
            }


class Character(InstructionGroup):
    """Character draws the character, handles audio data, and draws bubbles behind the character"""
    def __init__(self, spotify_player = None):
        super().__init__()

        self.audio = spotify_player

        self.character = CEllipse(cpos=(Window.width*3/4, Window.height/2), csize=(50, 50), sizesegments=20)
        self.color = Color(*(1, 1, 0))
        self.add(self.color)
        self.add(self.character)

        self.onbeat_bubbles = []
        self.offbeat_bubbles = []
        self.kill_list = []

        self.is_onbeat = False

        # Time keeping
        # self.duration = duration
        # self.speed = speed
        self.time = 0
        self.on_update(0)

    def spacebar(self, dt):
        self.time += dt
        if self.is_onbeat:
            for bubble in self.onbeat_bubbles:
                bubble.on_beat()
            bubble = OnBeatBubble(self.character.cpos, 20, (1,0,1), kSpeed)
            self.add(bubble)
            self.onbeat_bubbles.append(bubble)
        else:
            bubble = OffBeatSpray((self.character.cpos[0]/2, self.character.cpos[1]/2), [(1, 0, 0), (0, 1, 0)],
                                  animate=False)
            self.add(bubble)
            self.offbeat_bubbles.append(bubble)

    def on_up_press(self):
        current_pos = self.character.cpos
        if current_pos[1] < Window.height:
            self.character.cpos = (current_pos[0], current_pos[1] + 10)

    def on_down_press(self):
        current_pos = self.character.cpos
        if current_pos[1] > 0:
            self.character.cpos = (current_pos[0], current_pos[1] - 10)

    def on_update(self, dt):
        # self.time = self.audio.get_time()

        #if self.audio.is_onbeat():
        for bubble in self.kill_list:
            self.remove(bubble)

        if self.time > 4:
            self.is_onbeat = True
            self.time -= 4
        else:
            self.is_onbeat = False

        for bubble in self.onbeat_bubbles + self.offbeat_bubbles:
            bubble.on_update(dt)

        for bubble in self.onbeat_bubbles:
            if bubble.dot.cpos[0] < -20:
                self.kill_list.append(bubble)

        for bubble in self.offbeat_bubbles:
            if bubble.translate.x < -Window.width/2:
                self.kill_list.append(bubble)


class OnBeatBubble(InstructionGroup):
    def __init__(self, pos, radius, color, speed):
        super().__init__()

        self.original_pos = pos
        self.radius = radius

        # Color
        self.color = Color(*color)
        self.add(self.color)

        # Shape
        self.dot = CEllipse(cpos=pos, csize = (2*radius, 2*radius), sizesegments=20)
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

    def on_update(self, dt):
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

        self.time += dt
        # return self.radius_anim.is_active(self.time)


class OffBeatSpray(InstructionGroup):
    def __init__(self, pos, colors, bound=80, dot_size=5, num_dots=50, animate=False):
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
                              size=(self.rad, self.rad), segments=8) for i in range(self.num_dots)]

        for dot in self.dots:
            self.add(Color(*choice(self.colors)))
            self.add(dot)

        self.add(PopMatrix())

    def on_update(self, dt):
        self.time += dt
        if self.animate:
            for dot in self.dots:
                dot.pos = (dot.pos[0] + choice((-1, 1)) * random() * 2,
                           dot.pos[1] + choice((-1, 1)) * random() * 2)

        self.translate.x = self.translate.x - 10
        print(self.translate.x)


class TestWidget(BaseWidget):
    def __init__(self):
        super().__init__()

        self.spray = OffBeatSpray((300, 300), ((100, 0, 30), (0, 50, 200)), animate=True)
        self.canvas.add(self.spray)

        self.one_bubble = OnBeatBubble((Window.width*3/4,Window.height/2), 20, (1,1,0), 10000)
        self.canvas.add(self.one_bubble)

        self.time = 0

    def on_touch_move(self, touch):
        p = np.array(touch.pos) - np.array(self.spray.pos)
        self.spray.on_touch_move(p)

    def on_update(self):
        dt = kivyClock.frametime

        if self.time > 2:
            self.one_bubble.on_beat()
            self.time -= 2

        self.spray.on_update(dt)

        self.one_bubble.on_update(dt)

        self.time += dt


if __name__ == "__main__":
    run(TestWidget)