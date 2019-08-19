import copy
import numpy as np
from Point import Point

class Field(object):
    points = None

    def __init__(self, points=None):
        if (points is not None):
            self.set_points(points)

    def set_points(self, points):
        assert(type(points) == list)
        assert(type(points[0]) == Point)

        points = self._sort_points(points)
        self.points = copy.deepcopy(points)

    def draw(self, ax):
        east = [point.east for point in self.points]
        north = [point.north for point in self.points]
        ax.fill(east, north, edgecolor=[0,0,0], facecolor=[0.5, 0.5, 0.5], fill=False)
        ax.scatter(east, north, color=[0,0,0], marker='.', edgecolors='face')
        pass

    def _sort_points(self, points):
        return points