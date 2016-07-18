import math

from shapes.items import PointItem
from shapes.shape import Point
from transfromations.camera import ImageSurface, CameraProperties
from transfromations.perspective import Perspective
from utils.my_qt import *
import functools

import sys

from ui.motion_control import Ui_DockWidget
from utils.utils import to_mat

L_SPOTS = [QtCore.Qt.LeftDockWidgetArea, QtCore.Qt.RightDockWidgetArea, QtCore.Qt.BottomDockWidgetArea,
           QtCore.Qt.TopDockWidgetArea]


def update_layout(form, new_area):
    layout = form.groups_layout
    if (new_area in (QtCore.Qt.LeftDockWidgetArea, QtCore.Qt.RightDockWidgetArea)) == \
            (isinstance(layout, QtGui.QHBoxLayout)):
        # print 'changing layout'
        if isinstance(layout, QtGui.QHBoxLayout):
            new_layout = QtGui.QVBoxLayout()
        else:
            new_layout = QtGui.QHBoxLayout()
        w = layout.parent()
        while layout.count() > 0:
            c = layout.itemAt(0).widget()
            layout.removeWidget(c)
            new_layout.addWidget(c)
        w.removeItem(layout)
        w.addLayout(new_layout)
        form.groups_layout = new_layout


class ConstantView(QtGui.QGraphicsView):
    def __init__(self):
        super(ConstantView, self).__init__()
        self.setMouseTracking(True)

    def resizeEvent(self, QResizeEvent):
        size = QResizeEvent.size()
        new_scale = QtGui.QTransform.fromScale(size.width() / float(self.scene().sceneRect().width()),
                                               size.height() / float(self.scene().sceneRect().height()))
        self.setTransform(new_scale)
        super(ConstantView, self).resizeEvent(QResizeEvent)

    def mousePressEvent(self, QMouseEvent):
        print QMouseEvent.pos(), self.mapToScene(QMouseEvent.pos())
        super(ConstantView, self).mousePressEvent(QMouseEvent)


class Scene3D(object):
    DIR_LEFT = 'LEFT'
    DIR_RIGHT = 'RIGHT'
    DIR_UP = 'UP'
    DIR_DOWN = 'DOWN'
    DIR_FORWARD = 'FORWARD'
    DIR_BACKWARD = 'BACKWARD'

    def __init__(self, width, height):
        self._width = width
        self._height = height
        z1_surface = ImageSurface(to_mat(1, 1, 3), to_mat(1, 3, 3), to_mat(1, 1, 2))
        self._camera = CameraProperties(ImageSurface.EYE_DIRECTION_NEGATIVE, 1, z1_surface)
        # self.assertTrue((camera.eye() == to_mat(0, 2, 2.5)).all(), str(camera.eye()))
        self._perspective = Perspective(self._camera, width, height)
        self._scene = QtGui.QGraphicsScene()
        self._scene.setSceneRect(0, 0, width, height)
        self._scene.setItemIndexMethod(QtGui.QGraphicsScene.BspTreeIndex)

        for x in xrange(5, 15, 4):
            for y in xrange(-10, 10, 2):
                for z in xrange(-10, 10, 2):
                    s = '{},{},{}'.format(x, y, z)
                    self.add_item(PointItem(Point(to_mat(x, y, z), self._perspective),
                                            QtGui.QColor((20 * y) % 256, (20 * z) % 256, x),
                                            2, s))

    def connect_form(self, form):
        """
        :param form:
        :type form: Ui_DockWidget
        :return:
        """
        DELTA = 0.1
        RADIANS = 1. / 360. * math.pi * 2
        form.btn_camera_up.clicked.connect(functools.partial(self.move_camera, self.DIR_UP, DELTA))
        form.btn_camera_down.clicked.connect(functools.partial(self.move_camera, self.DIR_DOWN, DELTA))
        form.btn_camera_left.clicked.connect(functools.partial(self.move_camera, self.DIR_LEFT, DELTA))
        form.btn_camera_right.clicked.connect(functools.partial(self.move_camera, self.DIR_RIGHT, DELTA))
        form.btn_camera_backward.clicked.connect(functools.partial(self.move_camera, self.DIR_BACKWARD, DELTA))
        form.btn_camera_forward.clicked.connect(functools.partial(self.move_camera, self.DIR_FORWARD, DELTA))

        form.btn_camera_rotate_down.clicked.connect(functools.partial(self.rotate_camera, self.DIR_DOWN, RADIANS))
        form.btn_camera_rotate_up.clicked.connect(functools.partial(self.rotate_camera, self.DIR_UP, RADIANS))
        form.btn_camera_rotate_left.clicked.connect(functools.partial(self.rotate_camera, self.DIR_LEFT, RADIANS))
        form.btn_camera_rotate_right.clicked.connect(functools.partial(self.rotate_camera, self.DIR_RIGHT, RADIANS))

    def scene2d(self):
        return self._scene

    def add_item(self, item):
        self._scene.addItem(item)

    def move_camera(self, direction, pixels):
        if direction == self.DIR_LEFT:
            self._camera.move_left(pixels)
        elif direction == self.DIR_RIGHT:
            self._camera.move_right(pixels)
        elif direction == self.DIR_DOWN:
            self._camera.move_down(pixels)
        elif direction == self.DIR_UP:
            self._camera.move_up(pixels)
        elif direction == self.DIR_FORWARD:
            self._camera.move_forward(pixels)
        elif direction == self.DIR_BACKWARD:
            self._camera.move_backward(pixels)
        self._update_perspective()

    def rotate_camera(self, direction, radians):
        if direction == self.DIR_LEFT:
            self._camera.rotate_left(radians)
        elif direction == self.DIR_RIGHT:
            self._camera.rotate_right(radians)
        elif direction == self.DIR_DOWN:
            self._camera.rotate_down(radians)
        elif direction == self.DIR_UP:
            self._camera.rotate_up(radians)
        self._update_perspective()

    def _update_perspective(self):
        self._perspective = Perspective(self._camera, self._width, self._height)
        for item in self._scene.items():
            item.set_perspective(self._perspective)
        self._scene.update()


class MainWin(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent)
        self._dock = d = QtGui.QDockWidget("header", self)
        d.setAllowedAreas(reduce(lambda x, y: x | y, L_SPOTS, 0))
        self._control_form = form = Ui_DockWidget()
        form.setupUi(d)
        self.addDockWidget(L_SPOTS[2], d)
        d.dockLocationChanged.connect(functools.partial(update_layout, form))

        scene3d = Scene3D(800, 400)
        scene3d.connect_form(form)

        view = ConstantView()
        view.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        view.setScene(scene3d.scene2d())
        view.setRenderHint(QtGui.QPainter.Antialiasing)
        view.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        view.setViewportUpdateMode(QtGui.QGraphicsView.BoundingRectViewportUpdate)
        view.setDragMode(QtGui.QGraphicsView.RubberBandDrag)

        self.setWindowTitle("3D Viewer")
        self.setCentralWidget(view)


def main():
    app = QtGui.QApplication(sys.argv)
    w = MainWin()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
