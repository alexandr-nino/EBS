# -*- coding: utf-8 -*-
from ecs import System, Family, Component

Family._fields_ += [
    "Position",
    "Velocity",
    "LifeTime"
]


class PositionComponent(Component):
    family = Family.Position
    x = y = 0


class VelocityComponent(Component):
    family = Family.Velocity

    vx = 0
    vy = 1


class LifeTimeComponent(Component):
    family = Family.LifeTime

    delay = 5
    elapsed = 0


class MoveSystem(System):
    priority = 0
    require = Family.Position|Family.Velocity
    speed = 50

    def update(self, delta, entities):
        for e in entities:
            e[PositionComponent].x += e[VelocityComponent].vx*delta*self.speed
            e[PositionComponent].y += e[VelocityComponent].vy*delta*self.speed
            if e[PositionComponent].y >= 480:
                e[VelocityComponent].vy = -1
            elif e[PositionComponent].y <= 0:
                e[VelocityComponent].vy = 1


class LifeTimeSystem(System):
    priority = 1
    require = Family.LifeTime

    def update(self, delta, entities):
        for e in entities:
            e[LifeTimeComponent].elapsed += delta
            if e[LifeTimeComponent].elapsed >= e[LifeTimeComponent].delay:
                e.destroy()
