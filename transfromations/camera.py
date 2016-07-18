import math
import numpy

from transfromations.linear_transformations import RigidTransformation
from utils.utils import assert_3d, plane_coefs, normal_direction


class ImageSurface(object):
    EYE_DIRECTION_POSITIVE = 'POSITIVE'
    EYE_DIRECTION_NEGATIVE = 'NEGATIVE'

    def __init__(self, top_left, top_right, bottom_left):
        for p in (top_left, top_right, bottom_left):
            assert_3d(p)

        self.top_left = top_left
        self.top_right = top_right
        self.bottom_left = bottom_left
        self.bottom_right = self.bottom_left + self.left2right_vector()

        assert abs((self.left2right_vector().T * self.top2bottom_vector())[0, 0]) < 0.0001

    def left2right_vector(self):
        return self.top_right - self.top_left

    def top2bottom_vector(self):
        return self.bottom_left - self.top_left

    def orthogonal_direction(self):
        coefs = plane_coefs([self.top_left, self.top_right, self.bottom_left])
        n = coefs[:3]
        return normal_direction(n)

    def middle(self):
        return self.top_left + 0.5 * self.left2right_vector() + 0.5 * self.top2bottom_vector()

    def create_eye_at(self, direction, distance):
        assert direction in (self.EYE_DIRECTION_NEGATIVE, self.EYE_DIRECTION_POSITIVE)
        normal = self.orthogonal_direction()
        if direction == self.EYE_DIRECTION_NEGATIVE:
            sign = -1
        else:
            sign = 1
        for i in xrange(3):
            if abs(normal[i, 0]) > 0.0001:
                normal *= numpy.sign(normal[i, 0]) * sign
                break
        vector = normal * distance
        vector.resize((4, 1))
        return self.middle() + vector

    def move(self, vector):
        self.top_left += vector
        self.top_right += vector
        self.bottom_left += vector
        self.bottom_right += vector

    def transform(self, transformation):
        self.top_left = transformation.transform_point(self.top_left)
        self.top_right = transformation.transform_point(self.top_right)
        self.bottom_left = transformation.transform_point(self.bottom_left)
        self.bottom_right = transformation.transform_point(self.bottom_right)


class CameraProperties(object):
    def __init__(self, eye_direction, eye_distance, image_surface):
        """

        :param eye_direction:
        :param eye_distance:
        :param image_surface:
        :type image_surface: ImageSurface
        :return:
        """
        self._image_surface = image_surface
        self._eye = image_surface.create_eye_at(eye_direction, eye_distance)
        assert_3d(self._eye)

    def eye(self):
        return self._eye

    def image_surface(self):
        return self._image_surface

    def rotate_left(self, radians):
        self._rotate(RigidTransformation(radians, self.eye(), self._image_surface.top2bottom_vector()[:3]))

    def rotate_right(self, radians):
        self._rotate(RigidTransformation(-radians, self.eye(), self._image_surface.top2bottom_vector()[:3]))

    def rotate_up(self, radians):
        self._rotate(RigidTransformation(-radians, self.eye(), self._image_surface.left2right_vector()[:3]))

    def rotate_down(self, radians):
        self._rotate(RigidTransformation(radians, self.eye(), self._image_surface.left2right_vector()[:3]))

    def move_left(self, pixels):
        self._move_in_direction(self._image_surface.left2right_vector() * -1, pixels)

    def move_right(self, pixels):
        self._move_in_direction(self._image_surface.left2right_vector(), pixels)

    def move_up(self, pixels):
        self._move_in_direction(self._image_surface.top2bottom_vector() * -1, pixels)

    def move_down(self, pixels):
        self._move_in_direction(self._image_surface.top2bottom_vector(), pixels)

    def move_forward(self, pixels):
        self._move_in_direction(self._image_surface.middle() - self.eye(), pixels)

    def move_backward(self, pixels):
        self._move_in_direction(-self._image_surface.middle() + self.eye(), pixels)

    def _move_in_direction(self, direction, pixels):
        vector = pixels * normal_direction(direction)
        self._eye += vector
        self._image_surface.move(vector)

    def _rotate(self, rotation):
        self._image_surface.transform(rotation)

