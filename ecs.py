# -*- coding: utf-8 -*-
import array


class IntFlag(type):
    _fields_ = []

    @classmethod
    def __getattr__(cls, item):
        if item in cls._fields_:
            return 1 << cls._fields_.index(item)


class Family(metaclass=IntFlag):
    pass


class Component(object):
    owner = None
    family = 0

    _instances = None

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, id(self))

    def destroy(self):
        self.owner.remove_component(self)


class Entity(object):
    gm = None
    components = {}
    active = False
    dead = False
    id_ = -1

    def __init__(self, gm, id_=-1):
        self.id = id_
        self.gm = gm
        self.components = {}

    def destroy(self):
        self.dead = True

    def remove_component(self, component):
        del self.components[component.family]

    def add_component(self, component):
        component.owner = self
        self.components[component.family] = component

    def __getitem__(self, item):
        return self.components.get(item.family, None)

    def __contains__(self, item):
        return self[item.family] is not None

    def __repr__(self):
        return "Entity({}, {})".format(self.id, bin(self.gm.mask[self.id])[2:])


class System(object):
    require = 0
    gm = None
    priority = 0

    def update(self, delta, entities):
        raise RuntimeError("I'm abstract!")


class GameManager(object):
    entities = {}  # Entities
    systems = None  # Systems
    mask = array.array("l")
    free_list = array.array("l")
    next_uid = 0

    def __init__(self):
        self.entities = {}
        self.systems = []

    def filter(self, mask):
        return filter(lambda e: self.mask[e.id] & mask == mask, self.entities.values())

    def create_entity(self):
        if self.free_list:
            id_ = self.free_list.pop()
        else:
            id_ = self.next_uid
            self.next_uid += 1

        if id_ >= len(self.mask):
            try:
                self.mask.extend([0] * (id_ - len(self.mask) + 10))
            except MemoryError as ee:
                print(id_)
                raise ee

        e = Entity(self, id_)
        self.entities[id_] = e
        return e

    def assign(self, e, c):
        e.add_component(c)
        self.mask[e.id] += c.family

    def unassign(self, e, c):
        e.remove_component(c)
        self.mask[e.id] -= c.family

    def update(self, delta):
        for system in sorted(self.systems, key=lambda x: x.priority):
            entities = filter(lambda e: self.mask[e.id] & system.require == system.require, self.entities.values())
            system.update(delta, entities)

        for e_id in [e.id for e in self.entities.values() if e.dead]:
            self.remove_entity(id_=e_id)

        for e in filter(lambda x: not x.active, self.entities.values()):
            e.active = True

    def add_system(self, system):
        system.gm = self
        self.systems.append(system)

    def remove_system(self, system):
        self.systems.remove(system)

    def remove_entity(self, entity=None, id_=None):
        if entity is not None:
            id_ = entity.id
        elif id_ is None:
            raise RuntimeError("Entity or Id is required!")

        self.mask[id_] = 0
        self.free_list.append(id_)
        del self.entities[id_]
