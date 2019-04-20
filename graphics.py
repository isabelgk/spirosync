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


class Character(object):
    """Character draws the character, handles audio data, and draws bubbles behind the character"""
    def __init__(self, spotify_player = None):
        super().__init__()

        self.audio = spotify_player

        one_bubble = OnBeatBubble((Window.width*3/4,Window.height/2), 50, (1,1,0))

        # Time keeping
        self.duration = duration
        self.speed = speed
        self.time = 0
        self.on_update(0)

    def toggle_spacebar(self):
        pass

    def on_up_press(self):
        pass

    def on_up_release(self):
        pass

    def on_down_press(self):
        pass

    def on_down_release(self):
        pass

    def on_update(self, dt):
        #self.time = self.audio.get_time()
        self.time += dt


class OnBeatBubble(InstructionGroup):
    def __init__(self, pos, radius, color, speed):
        super().__init__()

        self.original_pos = pos

        # Color
        self.color = Color(*color)
        self.add(self.color)

        # Shape
        self.dot = CEllipse(cpos=pos, csize = (2*radius, 2*radius), sizesegments=20)
        self.add(self.dot)

        # Animation
        self.radius_anim = KFAnim((0, start_size), (duration, 0))
        self.pos_anim = KFAnim((0, pos[0]), (pos[0]*speed, 0))

        # Time keeping
        self.time = 0
        self.on_update(0)

    def on_update(self, dt):
        # rad = self.radius_anim.eval(self.time)
        # self.dot.csize = 2*rad, 2*rad

        pos = self.pos_anim.eval(self.time)
        self.dot.cpos = (pos, self.original_pos[1])

        self.time += dt
        # return self.radius_anim.is_active(self.time)


class OffBeatSpray(InstructionGroup):
    def __init__(self, pos, colors, bound=80, dot_size=5, num_dots=50, animate=False):
        """
        If the player hits the spacebar off the beat, a spray of dots will be placed onscreen.
        The colors map to the two most prominent pitch classes of that beat.

        :param pos: (tuple) center position of spray in pixels, e.g. (1040, 980)
        :param colors: (tuple) possible rgb tuples for the color, e.g. ((255, 255, 255), (155, 155, 251))
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

    def on_touch_move(self, pos):
        self.translate.x, self.translate.y = pos


class TestWidget(BaseWidget):
    def __init__(self):
        super().__init__()

        self.spray = OffBeatSpray((300, 300), ((100, 0, 30), (0, 50, 200)), animate=True)
        self.canvas.add(self.spray)

    def on_touch_move(self, touch):
        p = np.array(touch.pos) - np.array(self.spray.pos)
        self.spray.on_touch_move(p)

    def on_update(self):
        dt = kivyClock.frametime

        self.spray.on_update(dt)


if __name__ == "__main__":
    run(TestWidget)