import sys
sys.path.append('..')

from kivy.core.window import Window
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Rotate
from kivy.core.image import Image

from random import random, choice, randint

from constants import kPalette

import numpy as np

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