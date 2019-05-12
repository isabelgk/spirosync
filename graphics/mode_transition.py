import sys
sys.path.append('..')

from kivy.core.window import Window
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Rectangle
from kivy.core.image import Image


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