from utils.my_qt import *
from shapes.shape import Polygon, Line, Point
ABC = ''.join(chr(ord('A') + i) for i in xrange(26))
global_d = QtGui.QImage(QtCore.QSize(100, 100), QtGui.QImage.Format_ARGB32)


class PointItem(QtGui.QGraphicsItem):
    def __init__(self, point, color, radius, text, parent=None, scene=None):
        """

        :param point:
         :type point: Point
        :param color:
        :param radius:
        :param text:
        :param parent:
        :param scene:
        :return:
        """
        super(PointItem, self).__init__(parent, scene)
        self._point = point
        self._radius = radius
        self.color = color
        self._text = text

    def my_transform(self, transformation):
        self._point.transform(transformation)
        self.update()

    def boundingRect(self):
        p = self._point.viewed_qpoint()
        text_size = self._text_size()
        left = min(p.x() - text_size.width() / 2, p.x() - self._radius)
        right = max(p.x() + text_size.width() / 2, p.x() + self._radius)
        top = p.y() - self._radius - text_size.height()
        bottom = p.y() + self._radius
        return QtCore.QRectF(left, top, right, bottom)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(self._point.viewed_qpoint(), self._radius, self._radius)
        return path

    def paint(self, painter, option, widget):
        """
        :param painter:
         :type painter: QtGui.QPainter
        :param option:
        :param widget:
        :return:
        """
        # Body.
        font = QtGui.QFont()
        font.setBold(True)
        font.setPixelSize(self._radius * 2)
        painter.setFont(font)
        viewed_qpoint = self._point.viewed_qpoint()
        painter.drawText(self._text_position(viewed_qpoint), self._text)
        painter.setBrush(self.color)
        painter.drawPath(self.shape())

    def set_perspective(self, perspective):
        self._point.set_perspective(perspective)

    def _text_position(self, p):
        text_size = self._text_size()
        left = min(p.x() - text_size.width() / 2., p.x() - self._radius)
        top = p.y() - self._radius - text_size.height()
        return QtCore.QPointF(left, top)

    def _text_size(self):
        font = QtGui.QFont()
        font.setBold(True)
        font.setPixelSize(self._radius * 2)
        painter = QtGui.QPainter()
        painter.begin(global_d)
        painter.setFont(font)
        text_bounds = painter.boundingRect(0, 0, 100, 100, QtCore.Qt.AlignLeft, self._text)
        painter.end()
        return QtCore.QSize(text_bounds.width(), text_bounds.height())


class PolygonItem(QtGui.QGraphicsItem):
    def __init__(self, polygon, color, parent=None, scene=None):
        """
        :param polygon:
         :type polygon: Polygon
        :param color:
        :param parent:
        :param scene:
        :return:
        """
        super(PolygonItem, self).__init__(parent, scene)
        self.color = color
        self._polygon = polygon
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def my_transform(self, transformation):
        self.hide()
        self._polygon.transform(transformation)
        self.show()
        self.update()

    def boundingRect(self):
        return self._polygon.viewed_bounding_rect()

    def shape(self):
        return self._polygon.viewed_shape()

    def paint(self, painter, option, widget):
        pen = QtGui.QPen()
        pen.setWidth(1)
        pen.setBrush(QtGui.QColor("black"))
        painter.setBrush(self.color)
        painter.setPen(pen)
        painter.drawPath(self.shape())

    def set_perspective(self, new_perspective):
        self._polygon.set_perspective(new_perspective)




