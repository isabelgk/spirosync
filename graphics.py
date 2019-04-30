import sys
sys.path.append('..')
from common.core import *
from common.gfxutil import *

from kivy.core.window import Window, WindowBase
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate

from random import random, choice, randint

import colorsys
import numpy as np


# ==================================
# Constants
# ==================================

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


def generate_sub_palette(rgb, num_colors=16):
    """
    From one input color, create a list of colors (a sub-palette) close to that original.

    :param rgb: An RGB tuple as an initializer color
    :param num_colors: integer number of colors in output palette
    :return: list of RGB tuples of length num_colors
    """
    # Convert from RGB to HSV
    h, s, v = colorsys.rgb_to_hsv(*rgb)

    vs = np.linspace(0.7, 1.0, num_colors)
    ss = np.linspace(0.01, 1.0, num_colors)

    palette = [colorsys.hsv_to_rgb(h, ss[i], vs[i]) for i in range(num_colors)]

    return palette


# ==================================
# InstructionGroups
# ==================================
class User(InstructionGroup):
    """ The User handles the audio analysis data and can call methods on the visualizer modes. """
    def __init__(self, spotify_song):
        super().__init__()

        self.audio = spotify_song

        # index for current mode
        self.current_mode = 0


        # the mode for each section
        #self.section_modes = [int( random() * 3) for i in range(len(self.audio.get_current_track().get_sections()))]

        # FOR TESTING:
        self.section_modes = [2 for i in range(len(self.audio.get_current_track().get_sections()))]


        # list of all modes
        self.modes = [PulsingBar(), Tunnel(), SpectralBars()]

        #self.bar = PulsingBar()
        #self.spectra = SpectralBars()
        #self.add(self.bar)

        self.is_onbeat = False
        self.last_beat = 0


        # count the number of iterations that have been on beat
        self.num_beats = 0

        self.current_segment = 0
        self.current_section = 0

        # Time keeping
        # self.duration = duration
        # self.speed = speed
        self.time = 0
        self.on_update(0)

    def spacebar(self, time):
        # TODO: remove character
        self.time = time
        if self.is_onbeat and self.num_beats == 1:
            bubble = OnBeatBubble(self.character.cpos, 20, kPalette["red400"], kSpeed)
            self.add(bubble)
            self.onbeat_bubbles.add(bubble)
        else:
            bubble = OffBeatSpray((self.character.cpos[0]/2, self.character.cpos[1]/2),
                                  [kPalette["orange400"], kPalette["yellow400"]], bound=randint(10, 80),
                                  animate=True)
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
        self.is_onbeat = self.audio.get_current_track().on_beat(self.time, 0.1)

        section_index = self.audio.get_current_track().get_section_index(time)
        if section_index != self.current_section:
            # new section 

            old_mode = self.modes[self.section_modes[self.current_section]]
            new_mode = self.modes[self.section_modes[section_index]]
            self.remove(old_mode)
            self.add(new_mode)

            self.current_mode = self.section_modes[section_index]
            self.current_section = section_index



        if self.is_onbeat:
            self.num_beats += 1
        else:
            self.num_beats = 0

        if self.is_onbeat:
            self.modes[self.current_mode].on_beat()

        segment_index = self.audio.get_current_track().get_segment_index(time)
        if segment_index != self.current_segment:
            self.current_segment = segment_index
            data = self.audio.get_current_track().get_segments_data()[self.current_segment]
            self.modes[self.current_mode].on_segment(data)

        self.modes[self.current_mode].on_update(self.time)



class ProgressBar(InstructionGroup):
    """Graphics representing progress bar. Animates the fraction of the song that has played"""

    def __init__(self, sections, duration):
        super(ProgressBar, self).__init__()

        self.add(Color(rgb=kPalette['gray400']))
        self.length = Window.width * 0.9
        self.buffer = Window.width * 0.05

        self.sections = sections
        self.duration = duration
        self.section_color = []

        start_pos = self.buffer
        for section in self.sections:

            # For now, use a random color for the section.
            colors = list(kPalette.values())
            colors.remove(kPalette['gray50'])  # Save light gray for the progress mark.
            color = Color(rgb=choice(colors))
            self.section_color.append(color)
            self.add(color)

            section_length = section['duration'] * 1000
            bar_length = self.length * (section_length / self.duration)
            bar = Rectangle(pos=(start_pos, self.buffer), size=(bar_length, self.buffer))
            start_pos += bar_length
            self.add(bar)

        # Add a red progress mark.
        self.add(Color(rgb=kPalette['gray50']))
        self.progress_mark = Rectangle(pos=(self.buffer, self.buffer), size=(self.buffer / 10, self.buffer))
        self.add(self.progress_mark)

    def get_section_color(self, i):
        return self.section_color[i]

    def on_update(self, progress):
        self.progress_mark.pos = ((self.length * progress) + self.buffer, self.buffer)


# ==================================
# Visualizer modes
# ==================================

class PulsingBar(InstructionGroup):
    def __init__(self):
        super(PulsingBar, self).__init__()
        self.rectangles = []
        self.grow_anims = []
        self.colors = []

        self.time = 0
        self.rectangle = Rectangle(pos=(50,50), size=(50, 50))

        self.on_beat_time = None

    def on_beat(self):
        self.on_beat_time = self.time

    def on_segment(self, data):
        # data gives loudness_start, loudness_max_time, loudness_max, loudness_end, pitches, timbre
        pass

    def on_tatum(self):
        pass

    def on_update(self, time):
        # make rectangles if within 0.1 seconds of the beat
        if self.on_beat_time is not None and self.time - 0.1 < self.on_beat_time < self.time + 0.1:
            color = Color(*(random(),random(),random()))
            new_rect = Rectangle(pos=(0,Window.height/2), size=(Window.width, 0))
            grow = KFAnim((self.time, 0),(self.time + 0.01, Window.mouse_pos[1]-Window.height/2))

            mirror_rect = Rectangle(pos=(0,Window.height/2), size=(Window.width, 0))
            
            self.add(color)
            self.add(new_rect)
            self.add(mirror_rect)
            self.colors.append(color)
            self.rectangles.append(new_rect)
            self.rectangles.append(mirror_rect)
            self.grow_anims.append(grow)

        self.time += kivyClock.frametime
        # update rectangles and remove them if their height is 0
        remove_indices = []
        for i in range(len(self.colors)):
            new_height = self.grow_anims[i].eval(self.time)
            if new_height == 0:
                remove_indices.append(i)
            elif self.rectangles[2*i].size[1] != new_height:
                self.rectangles[2*i].size = (Window.width, new_height)
                self.rectangles[2*i+1].size = (Window.width, -new_height)
            else:
                # self.colors[i].a = 0.5
                self.grow_anims[i] = KFAnim((self.time, self.rectangles[2*i].size[1]), (self.time+1, 0))
        remove_indices.reverse()
        for i in remove_indices:
            mirror_rect = self.rectangles.pop(2*i+1)
            rectangle = self.rectangles.pop(2*i)
            self.grow_anims.pop(i)
            self.colors.pop(i)
            self.remove(mirror_rect)
            self.remove(rectangle)


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
    def __init__(self):
        super(Tunnel, self).__init__()

        self.colors = generate_sub_palette(kPalette["red400"])

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


class SpectralBars(InstructionGroup):
    def __init__(self):
        super().__init__()
        self.bars = []
        self.translates = []

        self.bar_width = Window.width / 36

        self.bar_height = Window.height / 2

        self.colors = generate_sub_palette(kPalette['teal400'], 12)

        for i in range(24):
            color = None
            if i < 12:
                color = self.colors[i]
            else:
                color = self.colors[23-i]
            self.add(Color(rgb=color))
            pos = ( (i * self.bar_width) + (6 * self.bar_width), Window.height/4)
            bar = Rectangle(pos = pos, size = (self.bar_width, self.bar_height))
            
            self.bars.append(bar)

            translate = Translate(0,0,0)

            self.translates.append(translate)

            self.add(PushMatrix())
            self.add(translate)
            self.add(bar)
            self.add(PopMatrix())

            self.segment_data = None

            self.mouse_distance_factor = [0 for i in range(24)]

    def on_beat(self):
        for i, t in enumerate(self.translates):
            if i < 12:
                t.x -= (50 + self.mouse_distance_factor[i])
            else:
                t.x += (50 + self.mouse_distance_factor[i])


    def on_segment(self, data):
        # data gives loudness_start, loudness_max_tim, loudness_max, loudness_end, pitches, timbre
        self.segment_data = data

        timbre = data['timbre']

        for i in range(12):
            left_translate = self.translates[i] 
            right_translate = self.translates[23-i] 

            left_translate.y = timbre[i] 
            right_translate.y = timbre[i] 


    def on_tatum(self):
        pass

    def on_update(self, time):
        for t in self.translates:
            y_diff = t.y
            x_diff = t.x
            t.x -= x_diff * 0.1
            t.y -= y_diff * 0.1
        x,y = Window.mouse_pos

        if y > self.bars[0].pos[1] and y < (self.bars[0].pos[1] + self.bar_height):
            for i,b in enumerate(self.bars):
                scale = Window.width
                d = 1/(b.pos[0] - Window.mouse_pos[0] + 1e-10) * scale
                self.mouse_distance_factor[i] = min(Window.width / 50, d)
        else:
            self.mouse_distance_factor = [0 for i in range(24)]



class OnBeatBubble(InstructionGroup):
    """Deprecated"""
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


class OffBeatSpray(InstructionGroup):
    """Deprecated"""
    def __init__(self, pos, colors, bound=50, dot_size=5, num_dots=10, animate=False):
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


if __name__ == "__main__":
    print(generate_sub_palette((0.9372549019607843, 0.3254901960784314, 0.3137254901960784)))