# -*- coding: utf-8 -*-
import weakref


#  makes something like C enum+std::bitset for Family definitions and use in masks
class Meta(type):
    def __getattr__(cls, item):
        if item in cls._fields_:
            return 1 << cls._fields_.index(item)


class Enum(object):
    _fields_ = []
    __metaclass__ = Meta


class Family(Enum):
    pass


class Component(object):
    owner = None
    family = 0

    _instances = None

    def __new__(cls, *args, **kwargs):
        if cls._instances is None:
            cls._instances = []
        instance = super(Component, cls).__new__(cls, *args, **kwargs)
        cls._instances.append(weakref.ref(instance, cls.__dealloc__))
        return instance

    @classmethod
    def __dealloc__(cls, weakref):
        cls._instances.remove(weakref)

    @classmethod
    def instances(cls):
        return cls._instances if cls._instances is not None else []

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, id(self))

    def update(self, delta):
        raise RuntimeError("""I'm abstract method!""")

    def destroy(self):
        self.owner.remove_component(self)


class Entity(object):
    gm = None
    components = {}
    active = False
    dead = False
    mask = 0

    def __init__(self, gm):
        self.gm = gm
        self.components = {}

    def destroy(self):
        self.dead = True

    def remove_component(self, component):
        self.mask -= component.family
        del self.components[component.__class__.__name__]

    def add_component(self, component):
        component.owner = self
        self.mask += component.family
        self.components[component.__class__.__name__] = component

    def __getitem__(self, item):
        return self.components.get(item.__name__, None)

    def __contains__(self, item):
        return self[item] is not None


class System(object):
    requires = 0  # unused yet
    gm = None
    priority = 0  # unused yet
    component = None

    def __init__(self, gm):
        self.gm = gm

    def update(self, delta):
        if isinstance(self.component, list):
            for component in self.component:
                for e in component.instances():
                    e().update(delta)
        else:
            for e in self.component.instances():
                e().update(delta)


class GameManager(object):
    e_list = None  # Entities
    s_list = None  # Systems
    render = None

    def __init__(self):
        self.e_list = []
        self.s_list = []
        self.render = None

    def set_render(self, render_system):
        self.render = render_system

    def get_render(self):
        return self.render

    def create_entity(self):
        e = Entity(self)
        self.e_list.append(e)
        return e

    def update(self, delta):
        for system in sorted(self.s_list, key=lambda x: x.priority):
            system.update(delta)

        for e in filter(lambda x: x.dead, self.e_list):
            e.components.clear()
            self.e_list.remove(e)

        for e in (e for e in self.e_list if not e.active):
            e.active = True

    def add_system(self, system):
        self.s_list.append(system)

    def remove_system(self, system):
        self.s_list.remove(system)

    def remove_entity(self, entity):
        self.e_list.remove(entity)
