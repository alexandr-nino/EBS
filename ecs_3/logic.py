# -*- coding: utf-8 -*-
from ecs_3.ecs import Family, Component, System
from ctypes import c_float

Family._fields_ += [
    "Position",
    "Velocity",
    "LifeTime"
]


class PositionComponent(Component):
    family = Family.Position

    _fields_ = [
        ("x", c_float),
        ("y", c_float),
    ]


class VelocityComponent(Component):
    family = Family.Velocity
    _fields_ = [
        ("x", c_float),
        ("y", c_float),
        ("speed", c_float)
    ]


class LifeTimeComponent(Component):
    family = Family.LifeTime
    _fields_ = [
        ("elapsed", c_float),
        ("delay", c_float)
    ]


class LifeTimeSystem(System):
    priority = 1
    requires = Family.LifeTime

    def update(self, gm, delta=0, *args):
        for e, (lc,) in gm.filter(self.requires):
            lc.elapsed += delta
            if lc.elapsed >= lc.delay:
                e.dead = True


class MoveSystem(System):
    priority = 0
    requires = Family.Position | Family.Velocity

    def update(self, gm, delta=0, *args):
        for e, (p, v,) in gm.filter(self.requires):
            p.x += v.x * delta * v.speed
            p.y += v.y * delta * v.speed
