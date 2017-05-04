Few implementations of Entity component system in Python.

**/ecs_1**:<br>
    Pure Python implementation with trick to store weakref to instances in cls._instances for "fast" iteration on it.<br>
    There are lags on destroy components.<br>
    Family class it's something like Enum and std::bitset in one. But unused here.<br>

**/ecs_2**:<br>
    Pure Python way without any dirty hacks. only list and dict. it's faster of all.<br>
    Implemented reusable ID.<br>

**/ecs_3**:<br>
    try to implement ecs via C/C++ data structures through ctypes.<br>
    All entities and components stored in Pool(cls) (like std::vector&lt;T&gt;)<br>
    Each pool store free ID list for reuse without memory allocation.<br>
    Now Family more like std::bitset. There is implemented Flag class for get index of 1 bit.<br>
        e.g. Family.Name -&gt; return 1&lt;&lt;index of Name in _fields_.<br>
             Family.Name.index -&gt; return index of 1 in bin data. 0001 =&gt; 3<br>
    It should be slowest and probably buggy.<br>