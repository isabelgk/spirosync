import sys
sys.path.append('..')
from common.core import *
from common.gfxutil import *
from common.audio import *
from common.mixer import *
from common.note import *
from common.wavegen import *
from common.wavesrc import *

from kivy.core.window import Window, WindowBase
from kivy.clock import Clock as kivyClock
from kivy.uix.label import Label
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate

from graphics import *


class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        self.character = Character()
        self.canvas.add(self.character)

        self.is_up = False
        self.is_down = False
        self.spacebar_down = False

        # Static text display
        self.info = topleft_label()
        self.add_widget(self.info)

    def on_key_down(self, keycode, modifiers):
        # up/down key will move character
        # spacebar will release bubbles
        if keycode[1] == 'up':
            self.is_up = True

        if keycode[1] == 'down':
            self.is_down = True

        if keycode[1] == 'spacebar':
            self.spacebar_down = True

    def on_key_up(self, keycode):
        # spacebar: stop releasing bubbles
        # up/down: stop moving
        if keycode[1] == 'up':
            self.is_up = False

        if keycode[1] == 'down':
            self.is_down = False

        if keycode[1] == 'spacebar':
            self.spacebar_down = False

    def on_update(self):
        dt = kivyClock.frametime
        # call Character onupdate 
        self.info.text = ''

        if self.is_up:
            self.character.on_up_press()
        if self.is_down:
            self.character.on_down_press()
        if self.spacebar_down:
            self.character.spacebar()

        self.character.on_update(dt)


if __name__ == "__main__":
    run(MainWidget)
