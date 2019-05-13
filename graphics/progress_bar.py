import sys
sys.path.append('..')

from kivy.core.window import Window
from kivy.graphics import Color, Line, Rectangle, RoundedRectangle, Bezier, SmoothLine
from kivy.graphics.instructions import InstructionGroup
from kivy.core.image import Image

from random import choice

from constants import kPalette

from utils import generate_sub_palette


class PitchPulse(InstructionGroup):
    """Graphics representing pitch line that goes through progress bar"""

    def __init__(self, buff):
        super(PitchPulse, self).__init__()
        self.buffer = buff
        width = Window.width / 36
        self.colors = []
        self.white_keys = []
        self.black_keys = []
        self.white_colors = []
        self.black_colors = []
        self.rectangles = []

        start_pos = width * 15
        for i in range(12, 24):
            color = Color(rgb = (1.0, 1.0, 1.0))
            if i in [13, 15, 18, 20, 22]:
                bar = Rectangle(pos=(start_pos - width/4, 0.96*Window.height - 0.75*buff), size=(width/2, 0.75*self.buffer))

                self.black_keys.append(bar)
                self.black_colors.append(color)

            else:
                bar = Rectangle(pos=(start_pos, 0.96*Window.height - 1.5*buff), size=(width, 1.5*self.buffer))
                start_pos += width
                self.white_keys.append(bar)
                self.white_colors.append(color)
            self.colors.append(color)
            self.rectangles.append(bar)
        
        for i in range(len(self.white_keys)):
            self.add(self.white_colors[i])
            self.add(self.white_keys[i])

        for i in range(len(self.black_keys)):
            # outline in background
            self.add(Color(rgb = (0.0, 0.0, 0.0)))
            pos = self.black_keys[i].pos
            size = self.black_keys[i].size
            background_rect = Rectangle(pos = (pos[0] - 5, pos[1] - 5), size = (size[0] * 1.1, size[1] * 1.1))

            self.add(background_rect)
            self.add(self.black_colors[i])
            self.add(self.black_keys[i])




    def on_segment(self, data, color):
        pitches = data['pitches']
        colors = generate_sub_palette(color, 12)
        sorted_pitches = sorted(enumerate(pitches), key=lambda x: x[1])

        for i in range(len(sorted_pitches)):
            ind, pitch = sorted_pitches[i]
            new_color = colors[11 - ind]
            self.colors[i].rgb = new_color


        

    def on_section(self, color):
        pass

    def on_update(self):
        '''
        for i in range(1, 24, 2):
            diff = self.line.points[i] - 1.5*self.bar_height
            #self.line.points[i] -= 0.5*diff
        '''
        pass


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
            # Do we want the rectangles to be rounded?
            bar = RoundedRectangle(pos=(start_pos, self.buffer), size=(bar_length, self.buffer))
            self.bars.append(bar)
            start_pos += bar_length
            self.add(bar)

        # Add a gray progress mark.
        self.add(Color(rgb=kPalette['gray50']))
        self.progress_mark = Rectangle(pos=(self.buffer, self.buffer), size=(self.buffer / 10, self.buffer))
        self.add(self.progress_mark)

        # make pitch pulse
        # progress bar starts at (self.buffer, self.buffer)
        self.pitch_pulse = PitchPulse(self.buffer)
        self.add(self.pitch_pulse)

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
        self.pitch_pulse.on_update()