import sys
sys.path.append('..')

from graphics import *
from spotify import *


class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        #self.audio = User("shann0nduffy")

        # Serena's account
        self.user = User('1235254187')

        self.audio = User("1235254187")
        self.sections = self.audio.get_current_track().get_sections()
        self.duration = self.audio.get_current_track().duration

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

        self.throttle = 0

        self.time = 0
        self.progress = 0


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
        # call Character onupdate

        fps = 0
        if self.throttle == 60:
            self.progress = self.audio.get_progress()
            self.time = self.audio.get_time()
            self.throttle = 0
        else:
            fps = kivyClock.get_fps()
            if fps == 0:
                fps = 60
            self.time += (1/fps * 1000)
            self.progress = self.time / self.audio.current_track.duration
            self.throttle += 1

        self.info.text = ''
        self.info.text += '%s\n' % str(self.character.character.cpos)
        self.info.text += str(self.time) + '\n'
        self.info.text += str(fps) + '\n'
        self.info.text += 'offbeat: %d\n' % len(self.character.offbeat_bubbles)
        self.info.text += 'onbeat: %d\n' % len(self.character.onbeat_bubbles)
        self.info.text += 'kill: %d' % len(self.character.kill_list)

        if self.is_up:
            self.character.on_up_press()
        if self.is_down:
            self.character.on_down_press()
        if self.spacebar_down:
            self.character.spacebar(self.time)

        self.character.on_update(self.time)

        self.bar.on_update(self.progress)


if __name__ == "__main__":
    run(MainWidget)
