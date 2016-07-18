import abc

import numpy


class Transformation(object):
    @abc.abstractmethod
    def transform_point(self, point):
        """
        :param point:
        :type point: numpy.matrix
        :return:
        """
        return point


