import sys
sys.path.append('..')
from common.gfxutil import *

from kivy.core.window import Window
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Rotate
from kivy.core.image import Image

from random import random
from utils import generate_sub_palette


class Kaleidoscope(InstructionGroup):
    def __init__(self, color):
        super(Kaleidoscope, self).__init__()
        self.color_palatte = generate_sub_palette(color) + [color]
        self.kaleidoscopes = []

    def on_bar(self):
        new_kaleidoscope = SingularKaleidoscope(self.color_palatte[int(random()*len(self.color_palatte))], Window.mouse_pos)
        self.add(Color(*(1,1,1)))
        self.add(new_kaleidoscope)
        self.kaleidoscopes.append(new_kaleidoscope)

    def on_beat(self):
        for kaleidoscope in self.kaleidoscopes:
            kaleidoscope.on_beat()

    def on_segment(self, data):
        # data gives loudness_start, loudness_max_time, loudness_max, loudness_end, pitches, timbre
        pass

    def on_tatum(self):
        pass

    def on_update(self, time):
        for kaleidoscope in self.kaleidoscopes:
            kaleidoscope.on_update(time)

class SingularKaleidoscope(InstructionGroup):
    def __init__(self, color, pos):
        super(SingularKaleidoscope, self).__init__()
        offset = Window.width * 0.05
        self.height = Window.height/3

        self.add(PushMatrix())
        self.background = CRectangle(pos=pos, size=(0,0),
                                    texture=Image('res/kaleidoscope/bw-circle.png').texture)
        self.add(self.background)

        self.rotate = Rotate(angle=0, origin=pos)
        self.add(self.rotate)

        self.star = CRectangle(pos=pos, size=(0,0),
                              texture=Image('res/kaleidoscope/bw-inner-star.png').texture)
        self.add(self.star)

        self.add(PopMatrix())

        self.circle = CEllipse(cpos=pos, csize=(0, 0))
        self.color = Color(*color)
        self.color.a = 0.5
        self.add(self.color)
        self.add(self.circle)

        self.size_grow = None

    def on_beat(self):
        self.rotate.angle += 10

    def on_segment(self, data):
        # data gives loudness_start, loudness_max_time, loudness_max, loudness_end, pitches, timbre
        pass

    def on_tatum(self):
        pass

    def on_update(self, time):
        if self.size_grow is None:
            self.size_grow = KFAnim((time,0), (time+1000,self.height))
        new_height = self.size_grow.eval(time)
        if new_height != self.height:
            self.background.set_csize((new_height, new_height))
            self.star.set_csize((new_height, new_height))
            self.circle.set_csize((new_height,new_height))
        pass


# Override Rectangle class to add centered functionality.
# use cpos and csize to set/get the rectangle based on a centered registration point
# instead of a bottom-left registration point
class CRectangle(Rectangle):
    def __init__(self, **kwargs):
        cpos = kwargs['pos']
        csize = kwargs['size']
        ctexture = kwargs['texture']
        super(CRectangle, self).__init__(pos=(cpos[0]-csize[0]/2,cpos[1]-csize[1]/2),size=(csize[0],csize[1]),texture=ctexture)

    def get_cpos(self):
        return (self.pos[0]+self.size[0]/2,self.pos[1]+self.size[1]/2)

    def set_cpos(self, p):
        self.pos = (p[0]-self.size[0]/2,p[1]-self.size[1]/2)

    def get_csize(self) :
        return self.size

    def set_csize(self, p) :
        cpos = self.get_cpos()
        self.size = p
        self.set_cpos(cpos)

    cpos = property(get_cpos, set_cpos)
    csize = property(get_csize, set_csize)






