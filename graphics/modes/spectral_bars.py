import sys
sys.path.append('..')

from kivy.core.window import Window
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, RoundedRectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate

from utils import generate_sub_palette


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
                color = self.colors[23 - i]
            self.add(Color(rgb=color))
            pos = ((i * self.bar_width) + (6 * self.bar_width), Window.height / 4)
            bar = RoundedRectangle(pos=pos, size=(self.bar_width, self.bar_height))

            self.bars.append(bar)

            translate = Translate(0, 0, 0)

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
            right_translate = self.translates[23 - i]

            left_translate.y = timbre[i]
            right_translate.y = timbre[i]

    def on_bar(self):
        pass

    def on_tatum(self):
        pass

    def on_update(self, time):
        for t in self.translates:
            y_diff = t.y
            x_diff = t.x
            t.x -= x_diff * 0.1
            t.y -= y_diff * 0.1
        x, y = Window.mouse_pos

        if y > self.bars[0].pos[1] and y < (self.bars[0].pos[1] + self.bar_height):
            for i, b in enumerate(self.bars):
                scale = Window.width
                d = 1 / (b.pos[0] - Window.mouse_pos[0] + 1e-10) * scale
                self.mouse_distance_factor[i] = min(Window.width / 50, d)
        else:
            self.mouse_distance_factor = [0 for i in range(24)]