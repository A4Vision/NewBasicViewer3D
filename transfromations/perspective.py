import numpy

from transfromations.camera import CameraProperties, ImageSurface
from unittest import TestCase
from utils.utils import assert_3d, EquationSystem, to_mat
from utils.my_qt import *


class Perspective(object):
    """
    A camera perspective.
    Assuming a camera stands on
    """

    def __init__(self, camera_properties, width_pixels, height_pixels):
        """

        :param camera_properties:
        :type camera_properties: CameraProperties
        :param width_pixels:
        :param height_pixels:
        :return:
        """
        self._width = width_pixels
        self._height = height_pixels
        self._camera = camera_properties
        # Mapping from the square in z=1 plane, to the image.
        # From: top-left=(-1, -1, 1) top-right=(1, -1, 1) bottom-left=(-1, 1, 1)  bottom-right=(1, 1, 1)
        #   To: top-left=(0, 0)      top-right=(WIDTH, 0) bottom-left=(0, HEIGHT) bottom-right=(WIDTH, HEIGHT)
        self._z1_to_image_scale = QtGui.QTransform.fromScale(width_pixels / 2.,
                                                             height_pixels / 2.).translate(1., 1.)
        self._surface2z1 = self._calculate_surface2z1(camera_properties)

    def perspective_of_point(self, point):
        """
        :param point:
        :type point: numpy.matrix
        :return:
        """
        assert_3d(point)

        above_surface = self._surface2z1 * point
        x, y, z = above_surface[0, 0], above_surface[1, 0], above_surface[2, 0]
        if z <= 0:
            return QtCore.QPointF(-1., -1.)
        else:
            on_surface = QtCore.QPointF(x / z, y / z)
            # move and rescale - map from the z=1 plane to
            return self._z1_to_image_scale.map(on_surface)

    def _calculate_surface2z1(self, camera_properties):
        # find T 3x3 such that:
        #           surface2z1 = (T Tc)
        #   where c = -eye.
        T_system = EquationSystem(3, 3)
        c = -camera_properties.eye()
        surface = camera_properties.image_surface()
        for source, target in zip([surface.top_left, surface.top_right, surface.bottom_left],
                                  [(-1, -1, 1), (1, -1, 1), (-1, 1, 1)]):
            moved = source + c
            for j in xrange(3):
                index_coef_pairs = [(T_system.index(j, t), moved[t, 0]) for t in xrange(3)]
                T_system.add_equation(index_coef_pairs, target[j])
        solution = T_system.get_solution()
        T = numpy.matrix([[0] * 3] * 3, dtype=numpy.float64)
        for i in xrange(3):
            for j in xrange(3):
                T[i, j] = solution[T_system.index(i, j)]
        # print 'T', T
        Tc = T * c[:3]
        res = numpy.matrix([[0] * 4] * 3, dtype=numpy.float64)
        for i in xrange(3):
            for j in xrange(3):
                res[i, j] = T[i, j]
        for j in xrange(3):
            res[j, 3] = Tc[j, 0]
        return res


class TestPerspective(TestCase):
    def test_identity_T(self):
        z1_surface = ImageSurface(to_mat(-1, -1, 1), to_mat(1, -1, 1), to_mat(-1, 1, 1))
        camera = CameraProperties(ImageSurface.EYE_DIRECTION_NEGATIVE, 1, z1_surface)
        perspective = Perspective(camera, 100, 300)
        for j in xrange(10):
            self.assertEqual(perspective.perspective_of_point(to_mat(0, 0, j + 1)), QtCore.QPointF(50, 150))
        self.assertEqual(perspective.perspective_of_point(to_mat(-1, -1, 1)), QtCore.QPointF(0, 0))

        self.assertEqual(perspective.perspective_of_point(to_mat(10, 14, 20)), QtCore.QPointF((10 / 20. + 1.) / 2. * 100,
                                                                                              (14 / 20. + 1.) / 2. * 300))

    def test_normal(self):
        z1_surface = ImageSurface(to_mat(1, 1, 3), to_mat(1, 3, 3), to_mat(1, 1, 2))
        camera = CameraProperties(ImageSurface.EYE_DIRECTION_NEGATIVE, 1, z1_surface)
        self.assertTrue((camera.eye() == to_mat(0, 2, 2.5)).all(), str(camera.eye()))
        perspective = Perspective(camera, 100, 300)
        self.assertEqual(perspective.perspective_of_point(to_mat(2, 2, 3.5)),
                         QtCore.QPointF(50, 0))
        self.assertEqual(perspective.perspective_of_point(to_mat(2, 4, 1.5)),
                         QtCore.QPointF(100, 300))
