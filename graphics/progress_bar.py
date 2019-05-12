import sys
sys.path.append('..')

from kivy.core.window import Window
from kivy.graphics import Color, Line, Rectangle, RoundedRectangle
from kivy.graphics.instructions import InstructionGroup

from random import choice

from constants import kPalette


class PitchPulse(InstructionGroup):
    """Graphics representing pitch line that goes through progress bar"""

    def __init__(self, bar_length, start_pos):
        super(PitchPulse, self).__init__()
        self.bar_height = start_pos
        self.add(Color(rgb=(1.0, 1.0, 1.0)))

        # generate 14 points to make up line
        self.points = [start_pos, start_pos] # left most point
        for i in range(1, 13):
            self.points.append(i * (bar_length+start_pos)/14)
            self.points.append(start_pos)

        # add rightmost point
        self.points.append(bar_length + start_pos)
        self.points.append(start_pos)

        # Bezier or line??
        self.line = Line(points=self.points, width=3, joint='round', cap='round')
        #self.line = Bezier(points=self.points)
        self.add(self.line)

    def on_segment(self, data):
        pitches = data['pitches']
        points = self.points.copy()

        # update the middle 12 points according to pitches
        for i in range(len(pitches)):
            y_pos = (self.bar_height * pitches[i]) + self.bar_height

            points[2*i+3] = y_pos

        self.line.points = points

    def on_update(self):
        for i in range(1, 24, 2):
            diff = self.line.points[i] - 1.5*self.bar_height
            #self.line.points[i] -= 0.5*diff


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
        self.pitch_line = PitchPulse(self.length, self.buffer)
        self.add(self.pitch_line)

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

    def on_segment(self, data):
        self.pitch_line.on_segment(data)

    def on_update(self, progress):
        self.progress_mark.pos = ((self.length * progress) + self.buffer, self.buffer)
        self.pitch_line.on_update()