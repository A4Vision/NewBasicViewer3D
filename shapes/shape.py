import abc

import numpy
from utils.my_qt import *
from utils.utils import average, assert_3d

ABC = ''.join(chr(ord('A') + i) for i in xrange(26))


class Shape(object):
    def __init__(self, perspective):
        """

        :param perspective:
        :type perspective: Perspective
        :return:
        """
        self._perspective = perspective

    def set_perspective(self, perspective):
        """

        :param perspective:
        :type perspective: Perspective
        :return:
        """
        self._perspective = perspective

    @abc.abstractmethod
    def transform(self, transformation):
        """
        :param transformation:
        :type transformation: Transformation
        :return:
        """
        pass


class Point(Shape):
    def __init__(self, xyzw_matrix, perspective):
        self._matrix = numpy.matrix(xyzw_matrix, dtype=numpy.float64)
        assert_3d(self._matrix)
        super(Point, self).__init__(perspective)

    def transform(self, transformation):
        self._matrix = transformation.transform_point(self._matrix)

    def viewed_qpoint(self):
        return self._perspective.perspective_of_point(self._matrix)

    def point(self):
        return self._matrix


class MultiPoint(Shape):
    __metaclass__ = abc.ABCMeta

    def __init__(self, xyzw_matrices, perspective):
        super(MultiPoint, self).__init__(perspective)
        self._points = [Point(m, perspective) for m in xyzw_matrices]

    def mean(self):
        return average([p.point() for p in self._points])

    def transform(self, transformation):
        for p in self._points:
            p.transform(transformation)


class Polygon(MultiPoint):
    def viewed_qpolygon(self):
        viewed_points = [p.viewed_qpoint() for p in self._points]
        return QtGui.QPolygonF([p for p in viewed_points + viewed_points[:1]])


class Line(MultiPoint):
    def __init__(self, p1_matrix, p2_matrix, perspective):
        super(Line, self).__init__([p1_matrix, p2_matrix], perspective)

    def viewed_line(self):
        viewed1 = self._points[0].viewed_qpoint()
        viewed2 = self._points[1].viewed_qpoint()
        return QtCore.QLineF(viewed1, viewed2)
