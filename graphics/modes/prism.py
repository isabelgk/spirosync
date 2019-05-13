import sys
sys.path.append('..')
from common.gfxutil import *

from kivy.core.window import Window
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Line
from kivy.graphics import PushMatrix, PopMatrix, Rotate

from random import choice, randint

from utils import generate_sub_palette, centroid

import itertools
import numpy as np


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
                                           (self.time + self.anim_duration / 6, start_x + self.velocity[0],
                                            start_y + self.velocity[1]),
                                           (self.time + self.anim_duration / 2, start_x + self.velocity[0]/2,
                                            start_y + self.velocity[1]/2),
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
    def __init__(self, points, color, width=2, a=0.5):
        super(Edge, self).__init__()

        self.color = Color(*color)
        self.color.a = a
        self.add(self.color)

        self.line = Line(points=points, width=width)
        self.add(self.line)

        self.index = 0


class Prism(InstructionGroup):
    """
    Inspired by https://www.youtube.com/watch?v=T3dpoSzWCu4

    A complete graph that wobbles around and looks like a prism
    """
    def __init__(self, color):
        super(Prism, self).__init__()
        v = 8  # number of vertices

        self.rotate_flag = True
        self.beat = 0  # Helps with on_beat()

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
            x_pos = randint(int(Window.width * 0.25), int(Window.width * 0.7))
            y_pos = randint(int(Window.height * 0.3), int(Window.height * 0.7))
            pos = x_pos, y_pos

            # Object to draw on screen
            vertex = Vertex(pos=pos, rgb=self.vertex_colors[i], rad=self.vertex_rad)

            # Store in dictionary for fast vertex lookup based on position
            self.vertices[pos] = vertex

        self.centroid = centroid(list(self.vertices.keys()))
        self.angle = 0
        self.rotate = Rotate(origin=self.centroid, angle=self.angle)

        self.original_vertices = self.vertices.copy()

        # Create a list where each element is a 2-tuple of the vertex points
        self.edges = []
        self._gen_edges(self.vertices.keys())

        self.add(PushMatrix())
        self.add(self.rotate)
        self._add_objects()
        self.add(PopMatrix())

    def _remove_objects(self):
        """Remove all vertices and edges from the screen"""
        if self.rotate_flag:
            self.remove(self.rotate)
        for e in self.edges:
            self.remove(e)
        for vertex in self.vertices.values():
            self.remove(vertex)

    def _add_objects(self):
        """Add all vertices and edges to the screen"""
        if self.rotate_flag:
            self.add(PushMatrix())
            self.rotate = Rotate(origin=self.centroid, angle=self.angle)
            self.add(self.rotate)

        for e in self.edges:
            self.add(e)
        for v in self.vertices.values():
            self.add(v)

        if self.rotate_flag:
            self.add(PopMatrix())

    def _gen_edges(self, vertices):
        """
        Helper method to create a list where each element is a 2-tuple of the vertex points
        :param vertices: Coordinates of vertices (list)
        :return: None
        """
        edges = []
        edge_points = list(itertools.combinations(vertices, 2))

        if self.beat % 2 == 0:
            a = 0.4
        else:
            a = 0.8
        for i in range(len(edge_points)):
            edge = Edge(points=edge_points[i], color=self.edge_color, width=2, a=a)
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
        self.beat += 1
        self.angle += 3

        if self.beat % 2 == 0:
            a = 0.4
        else:
            a = 0.8
        for v in self.vertices.values():
            v.set_alpha(a)

    def on_segment(self, data):
        for v in self.vertices.values():
            v.on_segment()

    def on_tatum(self):
        for v in self.vertices.values():
            v.on_tatum()

    def on_bar(self):
        pass

    def on_update(self, time):
        """
        Called by User every frame
        - Updates the time and mouse position
        - Checks which vertices are touched by the mouse and bounces them when touched
        """
        self.time = time

        if self.rotate_flag:
            # We care about the mouse position relative to rotated coordinates: math.stackexchange.com/questions/1964905

            # R = rotation matrix
            theta = -self.angle * np.pi / 180
            R = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])

            # Translation of the origin
            b = np.array(self.centroid)
            pos = np.array(Window.mouse_pos)

            self.mouse_pos = np.dot(R, pos - b) + b

        else:
            self.mouse_pos = Window.mouse_pos

        self._remove_objects()
        self._update_vertices()
        self._gen_edges(self.vertices.keys())
        self._add_objects()