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


class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        # Static text display
        self.info = topleft_label()
        self.add_widget(self.info)

    def on_key_down(self, keycode, modifiers):
        # up/down key will move character
        # spacebar will release bubbles
        if keycode[1] == '.':
            pass

    def on_key_up(self, keycode):
        # spacebar: stop releasing bubbles
        # up/down: stop moving
        pass

    def on_update(self):
        # call Character onupdate 
        self.info.text = ''


if __name__ == "__main__":
    run(MainWidget)
