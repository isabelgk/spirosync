import sys
sys.path.append('..')
from common.gfxutil import *

from kivy.core.window import Window
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Rectangle

from random import random

from utils import generate_sub_palette


class PulsingBar(InstructionGroup):
    def __init__(self, color):
        super(PulsingBar, self).__init__()
        self.rectangles = []
        self.grow_anims = []
        self.colors = []
        self.color_palatte = generate_sub_palette(color)

        self.time = 0
        self.rectangle = Rectangle(pos=(50, 50), size=(50, 50))

        self.beat_flags = [False] * 4

        self.on_beat_time = None

    def on_bar(self):
        pass

    def on_beat(self):
        self.on_beat_time = self.time
        self.beat_flags = [False] * 4
        for i in range(len(self.colors) - 1, -1, -1):
            mirror_rect = self.rectangles.pop(2 * i + 1)
            rectangle = self.rectangles.pop(2 * i)
            color = self.colors.pop(i)
            self.remove(mirror_rect)
            self.remove(rectangle)
            self.remove(color)

    def on_segment(self, data):
        # data gives loudness_start, loudness_max_time, loudness_max, loudness_end, pitches, timbre
        pass

    def on_tatum(self):
        pass

    def on_update(self, time):
        # TODO: remove the following stuff?
        # make rectangles if within 0.1 seconds of the beat

        # if self.on_beat_time is not None and self.time - 0.05 < self.on_beat_time < self.time + 0.01:
        #     color = Color(*(self.color_palatte[int(random()*len(self.color_palatte))]))

        #     new_rect = Rectangle(pos=(0,Window.height/2), size=(Window.width, 0))
        #     grow = KFAnim((self.time, 0),(self.time, Window.mouse_pos[1]-Window.height/2))

        #     mirror_rect = Rectangle(pos=(0,Window.height/2), size=(Window.width, 0))

        #     self.add(color)
        #     self.add(new_rect)
        #     self.add(mirror_rect)
        #     self.colors.append(color)
        #     self.rectangles.append(new_rect)
        #     self.rectangles.append(mirror_rect)
        #     self.grow_anims.append(grow)

        # self.time += kivyClock.frametime
        # # update rectangles and remove them if their height is 0
        # remove_indices = []
        # for i in range(len(self.colors)):
        #     new_height = self.grow_anims[i].eval(self.time)
        #     if new_height == 0:
        #         remove_indices.append(i)
        #     elif self.rectangles[2*i].size[1] != new_height:
        #         self.rectangles[2*i].size = (Window.width, new_height)
        #         self.rectangles[2*i+1].size = (Window.width, -new_height)
        #     else:
        #         # self.colors[i].a = 0.5
        #         self.grow_anims[i] = KFAnim((self.time, self.rectangles[2*i].size[1]), (self.time+1, 0))
        # remove_indices.reverse()
        # for i in remove_indices:
        #     mirror_rect = self.rectangles.pop(2*i+1)
        #     rectangle = self.rectangles.pop(2*i)
        #     self.grow_anims.pop(i)
        #     self.colors.pop(i)
        #     self.remove(mirror_rect)
        #     self.remove(rectangle)

        self.time += kivyClock.frametime

        for color in self.colors:
            color.a /= 1.01

        if self.on_beat_time:
            beat_diff = self.time - self.on_beat_time
            rect_height = 0
            if beat_diff > 0 and not self.beat_flags[0]:
                self.beat_flags[0] = True
                rect_height = Window.mouse_pos[1] - Window.height / 2
            elif beat_diff > 0.1 and not self.beat_flags[1]:
                self.beat_flags[1] = True
                rect_height = (Window.mouse_pos[1] - Window.height / 2) * 3 / 4
            elif beat_diff > 0.2 and not self.beat_flags[2]:
                self.beat_flags[2] = True
                rect_height = (Window.mouse_pos[1] - Window.height / 2) / 2
            elif beat_diff > 0.3 and not self.beat_flags[3]:
                self.beat_flags[3] = True
                rect_height = (Window.mouse_pos[1] - Window.height / 2) / 4

            if rect_height != 0:
                color = Color(*(self.color_palatte[int(random() * len(self.color_palatte))]))
                new_rect = Rectangle(pos=(0, Window.height / 2), size=(Window.width, rect_height))
                mirror_rect = Rectangle(pos=(0, Window.height / 2), size=(Window.width, -rect_height))
                # fade = KFAnim((0,1),(0.5,0))

                self.add(color)
                self.add(new_rect)
                self.add(mirror_rect)
                # self.grow_anims.append(fade)
                self.colors.append(color)
                self.rectangles.append(new_rect)
                self.rectangles.append(mirror_rect)