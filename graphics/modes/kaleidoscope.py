import sys
sys.path.append('..')
from common.gfxutil import *

from kivy.core.window import Window
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Rotate
from kivy.core.image import Image


class Kaleidoscope(InstructionGroup):
    def __init__(self, color):
        super(Kaleidoscope, self).__init__()
        offset = Window.width * 0.05
        height = Window.height-2*offset

        self.add(PushMatrix())
        self.background = Rectangle(pos=((Window.width-height)/2,2*offset), size=(height, height),
                                    texture=Image('res/kaleidoscope/circle.png').texture)
        self.add(self.background)

        middle_y = 2*offset + height/2

        self.rotate = Rotate(angle=0, origin=(Window.width/2,middle_y))
        self.add(self.rotate)

        self.star = Rectangle(pos=((Window.width-height)/2,2*offset), size=(height, height),
                              texture=Image('res/kaleidoscope/weird_star.png').texture)
        self.add(self.star)

        self.add(PopMatrix())

        self.circle = CEllipse(cpos=(Window.width/2,middle_y), csize=(height,height))
        self.color = Color(*color)
        self.color.a = 0.5
        self.add(self.color)
        self.add(self.circle)

    def on_touch_move(self, touch):
        pass

    def on_beat(self):
        self.rotate.angle += 10

    def on_segment(self, data):
        # data gives loudness_start, loudness_max_time, loudness_max, loudness_end, pitches, timbre
        pass

    def on_tatum(self):
        pass

    def on_update(self, time):
        pass