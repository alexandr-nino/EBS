# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
from ebs import Component, GameManager, System
from math import sqrt
import random
import time


class TransformComponent(Component):
    position = QtGui.QVector3D(0, 0, 0)


class MoveComponent(Component):
    def __init__(self):
        self.speed = 50
        self.forward = QtGui.QVector3D(0, 1, 0)
        self.q = QtGui.QQuaternion.fromAxisAndAngle(QtGui.QVector3D(0, 0, 1), random.randint(-180, 180))

    def update(self, delta):
        self.owner[TransformComponent].position += self.get_forward() * self.speed * delta

    def get_forward(self):
        return self.q.rotatedVector(self.forward)


class DynamicRotationComponent(Component):
    def update(self, delta):
        self.owner[MoveComponent].q *= QtGui.QQuaternion.fromAxisAndAngle(QtGui.QVector3D(0, 0, 1), 90 * delta)


class LifeTimeComponent(Component):
    elapsed = 0
    delay = 1

    def update(self, delta):
        self.elapsed += delta
        if self.elapsed >= self.delay:
            self.owner.destroy()


class BulletRenderComponent(Component):
    def update(self, gc):
        gc.setPen(QtGui.QColor(200, 0, 0))
        gc.drawPoint(self.owner[TransformComponent].position.toPoint())
        gc.drawEllipse(self.owner[TransformComponent].position.toPoint(), 3, 3)


class GunComponent(Component):
    delay = 0.6

    def __init__(self):
        self.elapsed = 0

    def update(self, delta):
        self.elapsed += delta
        if self.elapsed >= self.delay:
            self.elapsed = 0

            position = QtGui.QVector3D(self.owner[TransformComponent].position)
            q = QtGui.QQuaternion(self.owner[MoveComponent].q)

            e = self.owner.gm.create_entity()
            t_c = TransformComponent()
            t_c.position = position + self.owner[MoveComponent].get_forward() * 15
            e.add_component(t_c)

            m_c = MoveComponent()
            m_c.speed = 300
            m_c.q = q
            e.add_component(m_c)

            e.add_component(LifeTimeComponent())
            e.add_component(BulletRenderComponent())

            c_c = CollisionComponent()
            c_c.collider = 3
            e.add_component(c_c)


class TankRenderComponent(Component):
    def update(self, gc):
        collision_component = self.owner[CollisionComponent]
        if collision_component is not None:
            r = collision_component.collider
        else:
            r = 1
        pos = self.owner[TransformComponent].position
        gc.drawPoint(pos.toPoint())
        gc.drawEllipse(pos.toPoint(), r, r)
        gc.drawLine(pos.toPoint(), (self.owner[MoveComponent].get_forward() * 10 + pos).toPoint())


# FPS Killer =)
class CollisionComponent(Component):
    collider = 10

    def update(self, delta):
        for e1 in self.owner.gm.e_list:
            for e2 in self.owner.gm.e_list:
                if e1 is e2:
                    continue
                tmp = e1[TransformComponent].position - e2[TransformComponent].position
                dist = sqrt(tmp.x()**2 + tmp.y()**2)
                if dist < e1[CollisionComponent].collider + e2[CollisionComponent].collider:
                    e1.destroy()
                    e2.destroy()


class UpdateSystem(System):
    component = [MoveComponent, GunComponent, LifeTimeComponent, DynamicRotationComponent, CollisionComponent]


class RenderSystem(System):
    component = [TankRenderComponent, BulletRenderComponent]


class Window(QtGui.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.gm = GameManager()
        self.gm.add_system(UpdateSystem(self.gm))
        self.gm.set_render(RenderSystem(self.gm))
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
            e_l_c = len(self.gm.e_list)
            print "FPS:", self.fps, "Entities:", e_l_c, "Componentns", len(
                self.gm.e_list[0].components) * e_l_c if self.gm.e_list else 0
            self.fps = 0
            self.last_fps = self.last_tick

    def mousePressEvent(self, event):
        pos = QtGui.QVector3D(event.pos())
        e = self.gm.create_entity()
        t_c = TransformComponent()
        t_c.position = pos
        e.add_component(t_c)

        e.add_component(MoveComponent())
        e.add_component(GunComponent())
        e.add_component(TankRenderComponent())
        e.add_component(DynamicRotationComponent())

        c_c = CollisionComponent()
        c_c.collider = 10
        e.add_component(c_c)

    def paintEvent(self, QPaintEvent):
        gc = QtGui.QPainter()
        gc.begin(self)
        self.gm.get_render().update(gc)
        gc.end()


app = QtGui.QApplication([])
w = Window()
w.resize(640, 480)
w.show()
app.exec_()
