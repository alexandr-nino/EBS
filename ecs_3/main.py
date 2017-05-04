# -*- coding: utf-8 -*-
import time

from PyQt5 import QtGui, QtCore, QtWidgets

from ecs_3.logic import *
from ecs_3.ecs import *


class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.gm = EntityManager()
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

        for i in range(100):
            e = self.gm.create_entity()

            pc = PositionComponent(x=pos.x() + i * 5, y=pos.y())
            vc = VelocityComponent(x=0.0, y=1.0, speed=30)
            lc = LifeTimeComponent(delay=5.0)

            self.gm.assign(e, pc)
            self.gm.assign(e, vc)
            self.gm.assign(e, lc)


    def paintEvent(self, QPaintEvent):
        gc = QtGui.QPainter()
        gc.begin(self)

        for e, (p,) in self.gm.filter(Family.Position):
            if p.y < self.size().height():
                gc.drawPoint(p.x, p.y)
        # TODO: Render

        gc.end()


app = QtWidgets.QApplication([])
w = Window()
w.resize(640, 480)
w.show()
app.exec_()
