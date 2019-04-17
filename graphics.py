"""Classes that inherit from InstructionGroups to build various spirographs"""

from common.gfxutil import *

from kivy.graphics import Color, Rectangle, Line
from kivy.graphics import Rotate, PushMatrix, PopMatrix
from kivy.graphics.instructions import InstructionGroup

import numpy as np


class SpirographBasic(InstructionGroup):
    """A spirograph toy is used to draw hypocycloids, and here we recreate that drawing."""
    def __init__(self, start_pos, hsv, radius, k, speed, duration, line_width):
        super().__init__()

        # Geometry
        self.color = Color(hsv=hsv)
        self.add(self.color)
        self.line_width = line_width
        self.r = radius
        self.k = k
        self.pos1 = start_pos
        self.pos2 = None

        # Time keeping
        self.duration = duration
        self.speed = speed
        self.time = 0
        self.on_update(0)

    def on_update(self, dt):
        # A hypocycloid's shape is determined by two parametric equations: http://mathworld.wolfram.com/Hypocycloid.html
        x = self.pos1[0] + self.r * (self.k - 1) * np.cos(self.time * self.speed) + \
            self.r * np.cos((self.k - 1) * self.time * self.speed)
        y = self.pos1[1] + self.r * (self.k - 1) * np.sin(self.time * self.speed) - \
            self.r * np.sin((self.k - 1) * self.time * self.speed)
        self.pos2 = x, y

        # Create a line between the last point and the next.
        line = Line(points=(self.pos1, self.pos2), width=self.line_width)
        self.add(line)

        # Set up for next time step.
        self.pos1 = self.pos2
        self.time += dt
        return self.time < self.duration


class FadingDot(InstructionGroup):
    def __init__(self, pos=(0, 0), start_size=20, duration=1):
        super().__init__()

        # Color
        self.color = Color(hsv=(pos[0]/Window.width, 1, 1))
        self.color.a = 0.6
        self.add(self.color)

        # Shape
        self.dot = CEllipse(cpos=pos, segments=20)
        self.dot.csize = (start_size, start_size)
        self.add(self.dot)

        # Animation
        self.radius_anim = KFAnim((0, start_size), (duration, 0))
        self.pos_anim = KFAnim((0, pos[0], pos[1]), (duration*3, pos[0], 0))

        # Time keeping
        self.time = 0
        self.on_update(0)

    def on_update(self, dt):
        rad = self.radius_anim.eval(self.time)
        self.dot.csize = 2*rad, 2*rad

        pos = self.pos_anim.eval(self.time)
        self.dot.cpos = pos

        self.time += dt
        return self.radius_anim.is_active(self.time)