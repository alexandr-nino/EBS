# -*- coding: utf-8 -*-
"""
Implementation of ecs with ctypes data.
All data stored in Pool. Pool implemented like std::vector<T> on ctypes.Array.
It slow and probably buggy.
"""
from ctypes import *
import array

MAX_COMPONENTS = 8
INVALID_ID = 0


class Flag(int):
    def index(self):
        return bin(self)[::-1].find("1")

    index = property(fget=index)


class IntFlag(type):
    _fields_ = []

    @classmethod
    def __getattr__(cls, item):
        if item in cls._fields_:
            return Flag(1 << cls._fields_.index(item))


class Family(metaclass=IntFlag):
    pass


class Pool(object):
    __slots__ = ["items", "free_list", "next_id", 'cls']

    def __init__(self, cls, alloc=10):
        self.next_id = 1
        self.free_list = array.array("l")
        self.cls = cls
        self.items = (cls * alloc)()

    def resize(self, n):
        new_data = (self.cls * n)()
        memmove(new_data, byref(self.items), sizeof(self.items))
        self.items = new_data

    def add(self, item):
        if self.free_list:
            uid = self.free_list.pop()
        else:
            uid = self.next_id
            self.next_id += 1
        if uid >= len(self.items):
            self.resize(uid + 10)
        item.id = uid
        self.items[uid] = item

    def remove(self, item=None, uid=None):
        if item is not None:
            uid = item.id
        elif uid is None:
            raise ArgumentError("Item or uid is required!")
        self.free_list.append(uid)
        self.items[uid] = self.items[0]

    def __iter__(self):
        yield from (e for e in self.items if e.id != INVALID_ID)

    def __len__(self):
        c = 0
        for i in self.items:
            if i.id != INVALID_ID:
                c += 1
        return c

    size = property(fget=__len__)
    capacity = property(fget=lambda self: len(self.items))

    def __repr__(self):
        return "Pool({}, {})".format(self.cls.__name__, len(self))

    def __getitem__(self, index: int):
        return self.items[index]

    def __setitem__(self, index: int, value):
        self.items[index] = value


class Component(Structure):
    family = 0
    _fields_ = [
        ("id", c_int),
    ]

    def __repr__(self):
        return "{self.__class__.__name__}({self.id})".format(self=self)


class Entity(Structure):
    _fields_ = [
        ("id", c_int),
        ('mask', c_int),
        ("components", c_int * MAX_COMPONENTS),
        ("active", c_bool),
        ("dead", c_bool)
    ]

    def __repr__(self):
        return "{self.__class__.__name__}({self.id})".format(self=self)


class System(object):
    priority = 0
    requires = 0

    def update(self, gm, delta=0, *args):
        for entity, (components,) in gm.filter(self.requires):
            pass


class EntityManager(object):
    _fields_ = ["entities", "components", "systems"]

    def __init__(self):
        self.entities = Pool(Entity)
        self.components = {}
        self.systems = []

    def create_entity(self):
        e = Entity()
        self.entities.add(e)
        return e

    def remove(self, entity):
        for c in self.get_all_components(entity):
            self.unassign(entity, c)
        self.entities.remove(entity)

    def assign(self, e, c):
        if c.family not in self.components:
            self.components[c.family] = Pool(c.__class__)
        self.components[c.family].add(c)
        self.entities[e.id].mask += c.family
        self.entities[e.id].components[c.family.index] = c.id

    def get_component(self, entity, cls=None, family=None):
        if cls is not None:
            family = cls.family
        elif family is None:
            raise AttributeError("cls or family is required!")
        ec = self.entities[entity.id].components
        return self.components[family][ec[family.index]]

    def get_all_components(self, entity):
        ec = self.entities[entity.id].components
        return [self.components[1 << index][uid]
                for index, uid in enumerate(ec)
                if uid != INVALID_ID
                ]

    def unassign(self, e, c):
        self.entities[e.id].mask -= c.family
        e.components[c.family.index] = 0
        self.components[c.family].remove(c)

    def filter(self, mask):
        for e in filter(lambda x: x.id != INVALID_ID, self.entities):
            if not e.active or e.dead:
                continue
            if e.mask & mask == mask:
                yield e, [self.components[1 << index][uid]
                          for index, uid in enumerate(e.components)
                          if (1 << index) & mask == (1 << index) and e.active and not e.dead]

    add_system = lambda self, system: self.systems.append(system)
    remove_system = lambda self, system: self.systems.remove(system)

    def update(self, delta):
        for s in sorted(self.systems, key=lambda x: x.priority):
            s.update(self, delta)

        for e in filter(lambda x: x.id != INVALID_ID, self.entities):
            if e.dead:
                self.remove(e)
            elif not e.active:
                self.entities[e.id].active = True
