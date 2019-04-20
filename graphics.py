"""Classes that inherit from InstructionGroups to build various spirographs"""

from common.gfxutil import *

from kivy.graphics import Color, Rectangle, Line
from kivy.graphics import Rotate, PushMatrix, PopMatrix
from kivy.graphics.instructions import InstructionGroup

import numpy as np


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






