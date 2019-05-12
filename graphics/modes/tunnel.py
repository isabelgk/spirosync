import sys
sys.path.append('..')
from common.gfxutil import *

from kivy.core.window import Window
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate

from utils import generate_sub_palette


class DotRing(InstructionGroup):
    """Used in the Tunnel. Based on the Flower InstructionGroup from lecture3.py"""
    def __init__(self, start_pos=(Window.width / 2, Window.height / 2), start_ind=0, colors=((0, 1, 0), (0, 0, 1)),
                 num_dots=8, dot_rad=30, ring_rad=60):
        super(DotRing, self).__init__()
        self.start_ind = start_ind
        self.colors = colors
        self.dot_rad = dot_rad

        self.start_pos = start_pos

        self.add(PushMatrix())
        self.add(Translate(*start_pos))

        # Each dot needs another rotation
        d_theta = 360. / num_dots

        # Rotates the whole ring
        self._angle = Rotate(angle=0)
        self.add(self._angle)

        # Scales the whole ring
        self._scale = Scale(origin=self.start_pos, xy=(1, 1))
        self.add(self._scale)

        # Translates the whole ring
        self._translate = Translate()
        self.add(self._translate)

        # Increment rotation to place each petal
        for n in range(num_dots):
            self.add(Rotate(angle=d_theta))
            self.add(Translate(ring_rad, 0))
            c = colors[(self.start_ind + n) % len(colors)]  # Iterate through the list of colors so each dot is new color
            self.add(Color(*c))
            self.add(CEllipse(cpos=(0, 0), csize=(self.dot_rad, self.dot_rad)))
            self.add(Translate(-ring_rad, 0))

        self.add(PopMatrix())

        self.progress = 1
        self.is_alive = True

    def on_update(self):
        if self.progress < 0.01:
            self.is_alive = False

    @property
    def angle(self):
        return self._angle.angle

    @angle.setter
    def angle(self, x):
        self._angle.angle = x

    @property
    def scale(self):
        return self._scale.xyz

    @scale.setter
    def scale(self, s):
        self._scale.origin = self._translate.xy
        self.progress *= s
        self._scale.xyz = self._scale.xyz[0] * s, self._scale.xyz[1] * s, self._scale.xyz[2] * s

    @property
    def translate(self):
        return self._translate.xy

    @translate.setter
    def translate(self, xy):
        self._scale.origin = xy
        self._translate.xy = xy[0] - self.start_pos[0], xy[1] - self.start_pos[1]


class Tunnel(InstructionGroup):
    """Recreating https://codepen.io/Mamboleoo/pen/mJWLVJ.js"""
    def __init__(self, color):
        super(Tunnel, self).__init__()

        self.colors = generate_sub_palette(color)

        self.num_dots = len(self.colors)
        self.dot_rad = 100
        self.ring_rad = Window.width / 2
        self.index = 0

        self.rings = set()
        self.rings_to_kill = set()

        self.pos = Window.mouse_pos

        self.time = 0

    def on_beat(self):
        r = DotRing(colors=self.colors,
                    num_dots=self.num_dots,
                    dot_rad=self.dot_rad,
                    ring_rad=self.ring_rad,
                    start_pos=self.pos,
                    start_ind=self.index)

        self.rings.add(r)
        self.add(r)
        self.index += 1
        self.index = self.index % len(self.colors)

    def on_segment(self, data):
        # data gives loudness_start, loudness_max_tim, loudness_max, loudness_end, pitches, timbre
        pass

    def on_tatum(self):
        pass

    def on_touch_move(self, touch):
        pass

    def on_update(self, time):
        for ring in self.rings_to_kill:
            self.rings.remove(ring)
            self.remove(ring)
        self.rings_to_kill.clear()

        for ring in self.rings:
            if not ring.is_alive:
                self.rings_to_kill.add(ring)
            ring.scale = 0.992
            ring.angle += 0.1

        self.time = time
        self.pos = Window.mouse_pos
