import math

from utils.my_qt import *
import numpy

from transfromations.transformations import Transformation
from utils.utils import assert_3d, normal_direction


class ProjectiveTransformation(Transformation):
    def __init__(self, matrix):
        self._matrix = numpy.matrix(matrix, dtype=numpy.float64)

    def transform_point(self, xyzw_matrix):
        assert_3d(xyzw_matrix)
        v = self._matrix * xyzw_matrix
        return v / v[3, 0]


class TranslationTransformation(ProjectiveTransformation):
    """
    Simple move transformation.
    """

    def __init__(self, x, y, z):
        super(TranslationTransformation, self).__init__(numpy.matrix([[1, 0, 0, x],
                                                                      [0, 1, 0, y],
                                                                      [0, 0, 1, z],
                                                                      [0, 0, 0, 1]]))


class RigidTransformation(ProjectiveTransformation):
    def __init__(self, theta, center, vector):
        assert_3d(center)
        assert vector.shape == (3, 1)
        direction = normal_direction(vector)
        w = math.cos(theta / 2.)
        v = math.sin(theta / 2.) * direction
        x, y, z = v.T.tolist()[0]
        v_x = numpy.matrix([[0, -z, y],
                            [z, 0, -x],
                            [-y, x, 0]])
        I = numpy.matrix(numpy.identity(3))
        R = I + 2 * w * v_x + 2 * v_x * v_x
        c = center[:3]
        t = c - R * c
        m = numpy.matrix(numpy.zeros((4, 4), dtype=numpy.float64))
        for i in xrange(3):
            for j in xrange(3):
                m[i, j] = R[i, j]
            m[i, 3] = t[i, 0]
        m[3, 3] = 1.
        super(RigidTransformation, self).__init__(m)


