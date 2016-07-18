from unittest import TestCase

import math
import numpy


def average(l):
    if len(l) == 0:
        return 0
    else:
        s = l[0]
        for i in l:
            s += i
        return s / float(len(l))


def normal_direction(vector):
    return vector / math.sqrt(numpy.square(vector).sum())


def assert_3d(p):
    assert isinstance(p, numpy.matrix)
    assert p.shape == (4, 1)
    assert abs(p[3, 0] - 1) < 0.0001


class EquationSystem(object):
    """
    linear Equation system on a linear transformation.
    May be used to find a linear transformation under linear constraints.
    """
    def __init__(self, n_rows, n_columns):
        self._eqs = []
        self._b = []
        self._n_columns = n_columns
        self._n_rows = n_rows

    def index(self, i, j):
        return i * self._n_columns + j

    def add_equation(self, index_coef_pairs, b_value):
        self._b.append(b_value)
        self._eqs.append(self._create_eq(index_coef_pairs))

    def _create_eq(self, index_coef):
        res = [0] * self._n_columns * self._n_rows
        for index, coef in index_coef:
            res[index] = coef
        return res

    def get_solution(self):
        assert len(self._eqs) == self._n_columns * self._n_rows
        m = numpy.matrix(self._eqs)
        b = numpy.matrix(self._b).T
        matrix = numpy.linalg.solve(m, b)
        return matrix.T.tolist()[0]


def plane_coefs(points):
    for p in points:
        assert_3d(p)
    assert len(points) == 3
    eqs = numpy.matrix([[0] * 4] * 4, dtype=numpy.float64)
    for i, p in enumerate(points):
        for j in xrange(4):
            eqs[i, j] = p[j]
    for j in xrange(4):
        eqs[3, j] = numpy.random.random()
    b = numpy.matrix([[0.], [0.], [0.], [1.]])
    res = numpy.linalg.solve(eqs, b)
    res /= min([t[0, 0] for t in abs(res) if t[0, 0] > 0])
    return res


def to_mat(x, y, z):
    return numpy.matrix([[x, y, z, 1.]], dtype=numpy.float64).T


class TestPlaneCoefs(TestCase):
    def test1(self):
        for l_points in [[to_mat(0, 0, 1), to_mat(0, 1, 1), to_mat(1, 0, 1)],
                           [to_mat(0, 0, 1), to_mat(0, 1, 1), to_mat(0, 0, 0)],
                           [to_mat(1, 2, 0), to_mat(1, 1, 1), to_mat(0, 0, 10)]]:
            coefs = plane_coefs(l_points)
            for point in l_points:
                self.assertAlmostEqual(numpy.square(coefs.T * point).sum(), 0, delta=0.0001)