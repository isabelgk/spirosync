import sys
sys.path.append('..')

from graphics import *
from spotify import *


class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        self.audio = User("isabelkaspriskie")
        self.sections = self.audio.get_current_song().get_sections()
        self.duration = self.audio.get_current_song().duration

        self.bar = ProgressBar(self.sections, self.duration)
        self.canvas.add(self.bar)

        self.character = Character(self.audio)
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
        self.info.text += '%s' % str(self.character.character.cpos)

        if self.is_up:
            self.character.on_up_press()
        if self.is_down:
            self.character.on_down_press()
        if self.spacebar_down:
            self.character.spacebar(dt)

        self.character.on_update(dt)

        progress = self.audio.get_progress()

        self.bar.on_update(progress)


if __name__ == "__main__":
    run(MainWidget)
