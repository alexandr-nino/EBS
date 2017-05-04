Few implementations of Entity component system in Python.

ebs.py:
    Pure Python implementation with trick to store weakref to instances in cls._instances for "fast" iteration on it.
    There are lags on destroy components.

    Family class it's something like Enum and std::bitset in one. But unused here.

ecs.py:
    Pure Python way without any dirty hacks. only list and dict. it's faster of all.
    Implemented reusable ID.

ecs_ctypes.py:
    try to implement ecs via C/C++ data structures through ctypes.
    All entities and components stored in Pool(cls) (like std::vector<T>)
    Each pool store free ID list for reuse without memory allocation.
    Now Family more like std::bitset. There is implemented Flag class for get index of 1 bit.
        e.g. Family.Name -> return 1<<index of Name in _fields_.
             Family.Name.index -> return index of 1 in bin data. 0001 => 3
    It should be slowest and probably buggy.