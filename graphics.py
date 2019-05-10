"""InstructionGroups for graphical elements of the visualizer widget"""
import sys
sys.path.append('..')
from common.core import *
from common.gfxutil import *

from kivy.core.window import Window, WindowBase
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
from kivy.core.image import Image

from random import random, choice, randint, shuffle

from constants import kPalette
from utils import generate_sub_palette

import itertools
import numpy as np


class User(InstructionGroup):
    """ The User handles the audio analysis data and can call methods on the visualizer modes. """
    def __init__(self, spotify_song, progress_bar):
        super().__init__()

        self.audio = spotify_song
        self.progress_bar = progress_bar

        num_sections = len(self.audio.get_current_track().get_sections())

        # list of all background "shape" categories
        self.backgrounds = ["a", "b", "c", "d"]

        # the background for each section is random
        self.section_backgrounds = [int(random() * len(self.backgrounds)) for _ in range(num_sections)]

        # instance of current background
        self.current_background = None

        # list of all modes
        # self.modes = [PulsingBar, Tunnel, SpectralBars, Prism, Kaleidoscope]
        self.modes = [Prism, Prism]
        # the mode for each section
        self.section_modes = [int( random() * len(self.modes)) for i in range(len(self.audio.get_current_track().get_sections()))]
        # self.section_modes = [4 for i in range(len(self.audio.get_current_track().get_sections()))]

        # instance of current mode
        self.current_mode = None

        self.is_onbeat = False
        self.last_beat = 0

        self.in_transition = False
        self.transition_time = 2000  # ms

        # count the number of iterations that have been on beat
        self.num_beats = 0

        self.current_segment = 0
        self.current_section = -1

        # Time keeping
        self.time = 0
        self.on_update(0)

        self.play = True

    def play(self):
        self.play = True

    def pause(self):
        self.play = False

    def spacebar(self):
        if self.play:
            self.play = False
        else:
            self.play = True

    def update_progress_bar(self, progress_bar):
        self.progress_bar = progress_bar
        
    def on_touch_move(self, touch):
        if self.current_mode:
            self.current_mode.on_touch_move(touch)

    def on_update(self, time):
        self.time = time

        self.is_onbeat = self.audio.get_current_track().on_beat(self.time, 0.1)

        section_index = self.audio.get_current_track().get_section_index(time)

        if section_index == -1:
            return

        time_to_next = self.audio.get_current_track().get_time_to_next_section(time)

        if time_to_next < self.transition_time/1000 and not self.in_transition and time_to_next != -1:
            self.in_transition = True

            new_background = AmbientBackgroundBlobs(shape=choice(self.backgrounds))
            if self.current_background:
                self.remove(self.current_background)
            self.add(new_background)

            self.current_background = new_background

            color = self.progress_bar.get_section_color(section_index + 1)
            shuffle(self.modes)
            new_mode = ModeTransition(color, self.modes[0], self.modes[1], self.time, self.transition_time)

            if self.current_mode:
                self.remove(self.current_mode)
            self.add(new_mode)

            self.current_mode = new_mode
            self.current_section = section_index + 1

        elif section_index != self.current_section and not self.in_transition and section_index != -1:
            self.in_transition = True

            new_background = AmbientBackgroundBlobs(shape=choice(self.backgrounds))
            if self.current_background:
                self.remove(self.current_background)
            self.add(new_background)

            self.current_background = new_background

            color = self.progress_bar.get_section_color(section_index)
            shuffle(self.modes)
            new_mode = ModeTransition(color, self.modes[0], self.modes[1], self.time, self.transition_time)

            if self.current_mode:
                self.remove(self.current_mode)
            self.add(new_mode)

            self.current_mode = new_mode
            self.current_section = section_index


        self.in_transition = self.current_mode.in_transition(self.time, self.transition_time)


        # if section_index != self.current_section:
        #     # new section 
        #     # print(section_index)
        #     new_mode = self.modes[self.section_modes[section_index]](self.progress_bar.get_section_color(section_index))
        #     if self.current_mode:
        #         self.remove(self.current_mode)
        #     self.add(new_mode)

        #     self.current_mode = new_mode
        #     self.current_section = section_index

        if self.is_onbeat:
            self.num_beats += 1
        else:
            self.num_beats = 0

        if self.is_onbeat:
            self.current_mode.on_beat()

        segment_index = self.audio.get_current_track().get_segment_index(time)
        if segment_index != self.current_segment:
            self.current_segment = segment_index
            data = self.audio.get_current_track().get_segments_data()[self.current_segment]
            self.current_mode.on_segment(data)

        self.current_mode.on_update(self.time)
        self.current_background.on_update(self.time)


class ModeTransition(InstructionGroup):
    def __init__(self, color, mode1, mode2, start_time, transition_time):
        super(ModeTransition, self).__init__()
        self.transition_time = transition_time  * 1.5
        self.color = color
        self.mode1 = mode1
        self.mode2 = mode2
        self.start_time = start_time
        self.square_side = Window.width * 0.05

        # Dictionary mapping mode instance to corresponding texture
        self.mode_textures = {'Kaleidoscope': Image("res/Kaleidoscope.png").texture,
                              'Prism': Image("res/Prism.png").texture,
                              'PulsingBar': Image("res/PulsingBar.png").texture,
                              'SpectralBars': Image("res/SpectralBars.png").texture,
                              'Tunnel': Image('res/Tunnel.png').texture}

        self.new_mode = None

        self.left_color = Color(rgba =(1.0, 1.0, 1.0, 0.3))
        self.left = Rectangle(pos = (Window.width * 0.25, Window.height * 0.5 ), size = (Window.width * 0.1, Window.width * 0.1), texture = self.mode_textures[self.mode1.__name__] )
        self.add(self.left_color)
        self.add(self.left)

        self.right_color = Color(rgba = (1.0, 1.0, 1.0, 0.3))
        self.right = Rectangle(pos = (Window.width * 0.65, Window.height * 0.5 ), size = (Window.width * 0.1, Window.width * 0.1), texture = self.mode_textures[self.mode2.__name__] )
        self.add(self.right_color)
        self.add(self.right)

    def on_update(self, time):
        x_pos = Window.mouse_pos[0]

        if time > self.start_time + self.transition_time and not self.new_mode:
            if x_pos < Window.width / 2:
                self.new_mode = self.mode1(self.color)
            else:
                self.new_mode = self.mode2(self.color)
            self.remove(self.left)
            self.remove(self.right)
            self.add(Color(rgb=(1.0, 1.0, 1.0)))
            self.add(self.new_mode)
        elif time < self.start_time + self.transition_time:
            if x_pos < Window.width / 2:
                self.left_color.a = 0.8
                self.right_color.a = 0.3
            else:
                self.right_color.a = 0.8
                self.left_color.a = 0.3

        if self.new_mode:
            self.new_mode.on_update(time)

    def on_touch_move(self, touch):
        if self.new_mode:
            self.new_mode.on_touch_move(touch)

    def on_beat(self):
        if self.new_mode:
            self.new_mode.on_beat()

    def on_segment(self, data):
        if self.new_mode:
            self.new_mode.on_segment(data)

    def on_tatum(self):
        if self.new_mode:
            self.new_mode.on_tatum()

    def in_transition(self, time, transition_time):

        return time < self.start_time + transition_time


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
        self.bars = []
        start_pos = self.buffer

        colors = list(kPalette.values())
        colors.remove(kPalette['gray50'])  # Don't use the grays/brown in the section bars
        colors.remove(kPalette['blue_gray400'])
        colors.remove(kPalette['gray900'])
        colors.remove(kPalette['gray800'])
        colors.remove(kPalette['gray400'])
        colors.remove(kPalette['brown400'])

        section_loudness = [section['loudness'] for section in self.sections]

        for section in self.sections:
            # index into the color list based on how loud the current section is compared to the min and max loudness
            color_index = int(((section['loudness']-max(section_loudness))*(len(colors)-1)) / (min(section_loudness)-max(section_loudness)))
            self.section_color.append(colors[color_index])
            self.add(Color(rgb = colors[color_index]))

            section_length = section['duration'] * 1000
            bar_length = self.length * (section_length / self.duration)
            bar = Rectangle(pos=(start_pos, self.buffer), size=(bar_length, self.buffer))
            self.bars.append(bar)
            start_pos += bar_length
            self.add(bar)

        # Add a gray progress mark.
        self.add(Color(rgb=kPalette['gray50']))
        self.progress_mark = Rectangle(pos=(self.buffer, self.buffer), size=(self.buffer / 10, self.buffer))
        self.add(self.progress_mark)

    def update_song(self, sections, duration):
        self.sections = sections
        self.duration = duration
        self.remove(self.progress_mark)
        for b in self.bars:
            self.remove(b)
            self.bars = []
            self.section_colors = []

            start_pos = self.buffer
            for section in self.sections:

                # For now, use a random color for the section.
                colors = list(kPalette.values())
                colors.remove(kPalette['gray50'])  # Save light gray for the progress mark.
                color = choice(colors)
                self.section_color.append(color)
                self.add(Color(rgb = color))

                section_length = section['duration'] * 1000
                bar_length = self.length * (section_length / self.duration)
                bar = Rectangle(pos=(start_pos, self.buffer), size=(bar_length, self.buffer))
                self.bars.append(bar)
                start_pos += bar_length
                self.add(bar)
        self.add(Color(rgb=kPalette['gray50']))
        self.add(self.progress_mark)

    def get_section_color(self, i):
        return self.section_color[i]

    def on_update(self, progress):
        self.progress_mark.pos = ((self.length * progress) + self.buffer, self.buffer)


class FloatingShape(InstructionGroup):
    def __init__(self, cpos, dim, shape):
        super().__init__()

        self.shape = shape
        tex_file = 'res/background/%s%d.png' % (self.shape, randint(1, 4))

        self.buffer = dim[1] / 2

        self.dim = np.array(dim, dtype=np.float)
        self.cpos = cpos
        self.pos = np.array([cpos[0] - 0.5 * dim[0], cpos[1] - 0.5 * dim[1]])
        self.vel = np.array((choice([-1, 1]) * randint(50, 200), choice([-1, 1]) * randint(50, 200)), dtype=np.float)

        self.add(PushMatrix())

        self.rotate = Rotate(origin=self.pos, angle=randint(0, 359))
        self.add(self.rotate)

        self.shape = Rectangle(size=dim, texture=Image(tex_file).texture, pos=self.pos)
        self.add(self.shape)

        self.add(PopMatrix())

        self.time = 0
        self.on_update(0)

    def on_update(self, time):
        dt = (time - self.time) / 1000
        self.time = time

        # integrate vel to get pos
        self.pos += self.vel * dt
        self.rotate.angle += random()

        # collision with bottom
        if self.pos[1] < - self.buffer:
            self.vel[1] = -self.vel[1]
            self.pos[1] = - self.buffer

        # collision with top
        if self.pos[1] > Window.height + self.buffer:
            self.vel[1] = - self.vel[1]
            self.pos[1] = Window.height + self.buffer

        # collision with left side
        if self.pos[0] < -self.buffer:
            self.vel[0] = - self.vel[0]
            self.pos[0] = - self.buffer

        # collision with right side
        if self.pos[0] > Window.width + self.buffer:
            self.vel[0] = - self.vel[0]
            self.pos[0] = Window.width + self.buffer

        self.shape.pos = self.pos
        self.rotate.origin = self.pos

        return True


class AmbientBackgroundBlobs(InstructionGroup):
    """Light colored fading"""
    def __init__(self, shape, alpha=0.2, num_shapes=20):
        super().__init__()

        color = Color(*kPalette['gray800'])
        color.a = alpha
        self.add(color)

        self.blobs = []
        for i in range(num_shapes):
            rad = randint(int(Window.width/10), int(Window.width/3))
            pos = random() * Window.width, random() * Window.height
            blob = FloatingShape(pos, (rad, rad), shape)
            self.blobs.append(blob)
            self.add(blob)

    def on_update(self, time):
        for blob in self.blobs:
            # Move around randomly
            blob.on_update(time)


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

class PulsingBar(InstructionGroup):
    def __init__(self, color):
        super(PulsingBar, self).__init__()
        self.rectangles = []
        self.grow_anims = []
        self.colors = []
        self.color_palatte = generate_sub_palette(color)

        self.time = 0
        self.rectangle = Rectangle(pos=(50,50), size=(50, 50))

        self.beat_flags = [False] * 4

        self.on_beat_time = None

    def on_touch_move(self, touch):
        pass

    def on_beat(self):
        self.on_beat_time = self.time
        self.beat_flags = [False] * 4
        for i in range(len(self.colors)-1,-1, -1):
            mirror_rect = self.rectangles.pop(2*i+1)
            rectangle = self.rectangles.pop(2*i)
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
                rect_height = Window.mouse_pos[1]-Window.height/2
            elif beat_diff > 0.1 and not self.beat_flags[1]:
                self.beat_flags[1] = True
                rect_height = (Window.mouse_pos[1]-Window.height/2) * 3/4
            elif beat_diff > 0.2 and not self.beat_flags[2]:
                self.beat_flags[2] = True
                rect_height = (Window.mouse_pos[1]-Window.height/2) /2
            elif beat_diff > 0.3 and not self.beat_flags[3]:
                self.beat_flags[3] = True
                rect_height = (Window.mouse_pos[1]-Window.height/2) /4

            if rect_height != 0:
                color = Color(*(self.color_palatte[int(random()*len(self.color_palatte))]))
                new_rect = Rectangle(pos=(0,Window.height/2), size=(Window.width, rect_height))
                mirror_rect = Rectangle(pos=(0,Window.height/2), size=(Window.width, -rect_height))
                #fade = KFAnim((0,1),(0.5,0))
                
                self.add(color)
                self.add(new_rect)
                self.add(mirror_rect)
                #self.grow_anims.append(fade)
                self.colors.append(color)
                self.rectangles.append(new_rect)
                self.rectangles.append(mirror_rect)


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


class SpectralBars(InstructionGroup):
    def __init__(self, color):
        super(SpectralBars, self).__init__()
        self.bars = []
        self.translates = []

        self.bar_width = Window.width / 36

        self.bar_height = Window.height / 2

        self.colors = generate_sub_palette(color, 12)

        for i in range(24):
            color = None
            if i < 12:
                color = self.colors[i]
            else:
                color = self.colors[23-i]
            self.add(Color(rgb=color))
            pos = ( (i * self.bar_width) + (6 * self.bar_width), Window.height/4)
            bar = RoundedRectangle(pos = pos, size = (self.bar_width, self.bar_height))
            
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

    def on_touch_move(self, touch):
        pass

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


class Vertex(InstructionGroup):
    """Class to use in Prism"""
    def __init__(self, pos, rgb, rad, a=0.5):
        super(Vertex, self).__init__()
        self.pos = pos
        self.rad = rad

        self.color = Color(*rgb)
        self.alpha = a
        self.color.a = self.alpha
        self.add(self.color)

        self.dot = CEllipse(cpos=self.pos, csize=(2 * self.rad, 2 * self.rad), segments=50)
        self.add(self.dot)

        self.touched = False
        self.touched_anim = None

        self.time = 0
        self.anim_start_time = None
        self.anim_duration = 500  # ms
        self.bounce_distance = rad * 3

        self.quadrant = self._get_quadrant(self.pos)
        self.velocity = None
        self.set_velocity()

        self.on_update(0)

    @staticmethod
    def _get_quadrant(pos):
        """
        Given a position, determine which quadrant the point lies in, i.e.:
            2 | 1
            ------
            3 | 4
        """
        if pos[0] <= Window.width / 2:
            if pos[1] <= Window.height / 2:
                return 3
            else:
                return 2
        else:
            if pos[1] <= Window.height / 2:
                return 4
            else:
                return 1

    def set_velocity(self):
        if self.quadrant == 1:
            self.velocity = np.array([1, 1]) * self.bounce_distance
        elif self.quadrant == 2:
            self.velocity = np.array([-1, 1])* self.bounce_distance
        elif self.quadrant == 3:
            self.velocity = np.array([-1, -1])* self.bounce_distance
        else:
            self.velocity = np.array([1, -1])* self.bounce_distance

    def set_alpha(self, a):
        self.color.a = a

    def get_velocity(self):
        return self.velocity

    def on_beat(self):
        """
        Called by Prism, randomly moves a vertex

        :return: new position (tuple)
        """
        old_pos = self.dot.cpos

        # Randomly move the points and make sure they stay in the margins we set
        new_x = old_pos[0] + choice((-1, 1)) * randint(5, 15)
        if new_x < Window.width * 0.1:
            new_x = Window.width * 0.1
        elif new_x > Window.width * 0.9:
            new_x = Window.width * 0.9

        new_y = old_pos[1] + choice((-1, 1)) * randint(5, 15)
        if new_y < Window.height * 0.2:
            new_y = Window.height * 0.2
        elif new_y > Window.height * 0.8:
            new_y = Window.height * 0.8

        self.dot.cpos = new_x, new_y
        return new_x, new_y

    def on_touch(self):
        """Called by Prism when the mouse touches the vertex"""
        if not self.touched:
            if self.touched_anim is None:
                self.anim_start_time = self.time
                start_x, start_y = self.pos
                self.touched_anim = KFAnim((self.time, start_x, start_y),
                                           (self.time + self.anim_duration / 6, start_x + self.velocity[0], start_y + self.velocity[1]),
                                           (self.time + self.anim_duration, start_x, start_y))

    def set_pos(self, p):
        self.dot.pos = np.array(p) - self.rad

    def get_pos(self):
            return self.dot.pos

    def on_tatum(self):
        pass

    def on_segment(self):
        pass

    def on_update(self, time):
        self.time = time

        if self.anim_start_time is not None and self.anim_start_time + self.anim_duration <= self.time:
            self.touched_anim = None
            self.anim_start_time = None

        if self.touched_anim is not None:
            self.pos = self.touched_anim.eval(self.time)
            self.dot.cpos = self.pos

        if self.touched:
            self.touched = False


class Edge(InstructionGroup):
    def __init__(self, points, color, width=1, a=0.5):
        super(Edge, self).__init__()

        self.color = Color(*color)
        self.color.a = a
        self.add(self.color)

        self.line = Line(points=points, width=width)
        self.add(self.line)

        self.index = 0

    def on_pulse(self):
        self.index += 1
        if self.index % 2 == 0:
            self.line.width /= 3
        else:
            self.line.width *= 3


class Prism(InstructionGroup):
    """
    Inspired by https://www.youtube.com/watch?v=T3dpoSzWCu4

    A complete graph that wobbles around and looks like a prism
    """
    def __init__(self, color):
        super(Prism, self).__init__()
        v = 8  # number of vertices

        self.vertex_rad = 20
        self.boundary = self.vertex_rad  # Radial boundary for registering a touch on a vertex

        # Generate RGB palette
        self.colors = generate_sub_palette(color, num_colors=v+3)
        self.edge_color = self.colors[-1]
        self.vertex_colors = self.colors[:-1]

        # Keep track of mouse position and time
        self.mouse_pos = Window.mouse_pos
        self.time = 0

        # Graphical elements (vertices and edges)
        self.vertices = {}
        for i in range(v):
            # Random position
            x_pos = randint(int(Window.width * 0.1), int(Window.width * 0.9))
            y_pos = randint(int(Window.height * 0.2), int(Window.height * 0.8))
            pos = x_pos, y_pos

            # Object to draw on screen
            vertex = Vertex(pos=pos, rgb=self.vertex_colors[i], rad=self.vertex_rad)

            # Store in dictionary for fast vertex lookup based on position
            self.vertices[pos] = vertex

        self.original_vertices = self.vertices.copy()

        # Create a list where each element is a 2-tuple of the vertex points
        self.edges = []
        self._gen_edges(self.vertices.keys())

        self._add_objects()

    def _remove_objects(self):
        """Remove all vertices and edges from the screen"""
        for e in self.edges:
            self.remove(e)
        for vertex in self.vertices.values():
            self.remove(vertex)

    def _add_objects(self):
        """Add all vertices and edges to the screen"""
        # First remove the edges and vertices from the screen
        for e in self.edges:
            self.add(e)
        for v in self.vertices.values():
            self.add(v)

    def _gen_edges(self, vertices):
        """
        Helper method to create a list where each element is a 2-tuple of the vertex points
        :param vertices: Coordinates of vertices (list)
        :return: None
        """
        edges = []
        edge_points = list(itertools.combinations(vertices, 2))
        for i in range(len(edge_points)):
            edge = Edge(points=edge_points[i], color=self.edge_color, width=2)
            edges.append(edge)
        self.edges = edges

    def _update_vertices(self):
        # Updated which vertices are touched
        touched = set()
        for v in self.vertices.keys():
            self.vertices[v].on_update(self.time)
            dot = np.array(v)
            dist = np.abs(np.linalg.norm(dot - np.array(self.mouse_pos)))
            if dist < self.boundary:
                # Vertex is touched
                self.vertices[v].on_touch()
                touched.add(self.vertices[v])

        # # For the touched vertices, evaluate their animations
        # # Move the vertices
        # for vertex in touched:  # Bounce the vertex away from the mouse when touched
        for vertex in self.vertices.values():
            new_pos = tuple(vertex.dot.cpos)
            coord_to_remove = None  # Can't remove an item while iterating through the dictionary
            for coord, obj in self.vertices.items():
                if vertex == obj:
                    coord_to_remove = coord
            self.vertices.pop(coord_to_remove)  # Now remove it
            self.vertices[new_pos] = vertex  # And replace it
            vertex.set_pos(new_pos)  # Change the position of the vertex too

    def on_beat(self):
        """Pulse the linewidth"""
        pass

    def on_segment(self, data):
        for v in self.vertices.values():
            v.on_segment()

    def on_tatum(self):
        for v in self.vertices.values():
            v.on_tatum()

    def on_touch_move(self, touch):
        pass

    def on_update(self, time):
        """
        Called by User every frame
        - Updates the time and mouse position
        - Checks which vertices are touched by the mouse and bounces them when touched
        """
        self.time = time
        self.mouse_pos = Window.mouse_pos

        self._remove_objects()
        self._update_vertices()
        self._gen_edges(self.vertices.keys())
        self._add_objects()


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

class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        self.kaleidoscope = Kaleidoscope()
        self.canvas.add(self.kaleidoscope)

        # Static text display
        self.info = topleft_label(font_filepath="res/font/CabinCondensed-Regular.ttf")
        self.add_widget(self.info)

        
    def on_key_down(self, keycode, modifiers):
        pass

    def on_touch_move(self, touch) :
        # apply rotation
        p = touch.pos
        self.kaleidoscope.on_touch_move(p)

    def on_update(self):
        pass


if __name__ == "__main__":
    run(MainWidget)
