# -*- coding: utf-8 -*-
import time

from PyQt5 import QtGui, QtCore, QtWidgets

from ecs_2.logic import *
from ecs_2.ecs import *


class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.gm = GameManager()
        self.gm.add_system(MoveSystem())
        self.gm.add_system(LifeTimeSystem())
        self.fps = 0

        self.t = QtCore.QTimer(self)
        self.t.timeout.connect(self.update)
        self.last_tick = self.last_fps = time.time()
        self.t.start()

    def update(self):
        delta = time.time() - self.last_tick
        self.last_tick = time.time()
        self.gm.update(delta)
        self.repaint()

        self.fps += 1
        if self.last_tick - self.last_fps >= 1.:
            fmt = "FPS: {}  Entities: {}"
            print(fmt.format(self.fps, len(self.gm.entities)))

            self.fps = 0
            self.last_fps = self.last_tick

    def mouseMoveEvent(self, event):
        pos = event.pos()

        for i in range(50):
            e = self.gm.create_entity()

            pc = PositionComponent()
            pc.x, pc.y = pos.x() + i * 5, pos.y()

            vc = VelocityComponent()
            vc.vx, pc.vy = 0, 1

            self.gm.assign(e, pc)
            self.gm.assign(e, vc)

            lc = LifeTimeComponent()
            lc.delay = 10
            self.gm.assign(e, lc)

    def paintEvent(self, QPaintEvent):
        gc = QtGui.QPainter()
        gc.begin(self)

        for e in self.gm.filter(Family.Position):
            if e[PositionComponent].y < self.size().height():
                gc.drawPoint(e[PositionComponent].x, e[PositionComponent].y)
        # TODO: Render

        gc.end()


app = QtWidgets.QApplication([])
w = Window()
w.resize(640, 480)
w.show()
app.exec_()
