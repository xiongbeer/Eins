快速上手
========

车辆
----

新建一辆车辆： ::

    import road
    car = road.Car()

需用户定义的车辆属性：

=============  ============  =======  ======
属性名          含义          初始值    单位
=============  ============  =======  ======
length         车辆长度        1.0     *m*
safedistance   最小安全车距     0.0     *m*
acc            加速度          1.0     *m/s^2*
slowacc        慢加速度        0.5     *m/s^2*
negacc         减速度          1.0     *m/s^2*
view           视野距离        0.0     *m*
speed          速度           0.0      *m/s*
=============  ============  =======  ======


.. note::
    * 不一定需要定义全部属性，根据要使用数学模型的需求来定义即可
    * 速度定义的含义是车辆的初始速度
    * 车辆在道路上运行时会具有许多其他的属性，详情请往后阅读

以NaSch模型为例，模拟现实生活中普通车辆时，可以定义如下： ::

    car.length       = 3.5
    car.acc          = 3.2
    car.negacc       = 3.0
    car.safedistance = 50.0

.. tip::
    合适的值可以查询国家的相关规定来得到


道路
----
道路具有非常多的属性和方法，我们慢慢道来

得到一条道路
^^^^^^^^^^^^

为了初始化一条道路，有3个参数是必不可少的：

 * 初始化的车辆 --- carbox
 * 道路长度 --- length
 * 道路的最大限定速度 --- vmax

其中carbox必须要符合特定的格式，由两层嵌套的list构成::

    [
        [car_1, car_2, ..., car_n],

        [car_1, car_2, ..., car_n],

        ...

        [car_1, car_2, ..., car_n]
    ]

可以想象为第一层这个整体就是整条道路，而道路中有N条车道即第一层里面的各个元素(list)，各个元素(list)里面的元素(Car)就是车辆

同时，有如下规定：
    * 在一条车道中，第n+1辆车一定位于第n辆车前方
    * 车道号从小到大对应着从左到右，比如 *lane_0* 对于 *lane_1* 是在左方， *lane_2* 对于 *lane_1* 是在右方
    * 同一条道路上的所有车道行驶方向相同
    * carbox第一层内的元素个数必须严格等于初始化时规定的车道数。比如车道数为3的道路，其carbox必须这样构成::

        [
            [...],
            [...],
            [...]
        ]

.. note::
    第二层中的元素可以为空，即那条车道上没有任何车辆

下面来举个简单的例子，初始化一条长度为500m，最大速度60km/h，车道为2,每条车道上有2辆车的道路::

    from road import *
    import copy
    vmax = 16.7             # 这里的单位为 m/s
    length = 500
    car1 = Car()
    car1.locate = 100.0     # 这里定义locate实际上是定义车辆的初始化所在的位置
    car1.lane = 0           # 定义车道标号
    car2 = Car()
    car2.locate = 300.0
    car2.lane = 0
    car3 = Car()
    car3.locate = 150.0
    car3.lane = 1
    car4 = Car()
    car4.locate = 250.0
    car4.lane = 1
    carbox = [[car1, car2], [car3, car4]]
    rd = ExecRoad(carbox=carbox, length=length, vmax=vmax)      # 得到一条道路

虽然的确得到了要的道路，但是过于繁琐，而且车辆数一多肯定不能这样手动的一辆一辆去创建


这里提供2个帮助新建用于初始化carbox的函数：

    *init_empty_road(lanes)*
          ------  用于初始化空的道路，需要的参数只有道路的车道数量

    *init_cars_distributed(length, carTemplateBox, carsNum=None, lanes=1, dis='normal', pers=None)*
          ------  可以按预定的格式初始化道路，必须的参数为分布长度、车辆模板

示例::

    from road import *
    import copy
    lanes = 3
    length = 1000
    vmax = 20
    carbox1 = init_empty_road(lanes)
    rd = ExecRoad(carbox=carbox1, length=length, vmax=vmax)                     # 空的道路
    rd1 = ExecRoad(carbox=copy.deepcopy(carbox1), length=length, vmax=vmax)     # 一定要记得使用deepcopy!!!不要直接重复使用!!!

    car = Car()    # 使用提供的初始化函数时不需要指定初始车道编号
    car.speed = vmax    # 定义车辆初始速度
    car.safedistance = 50
    car.length = 4
    car.acc = 3.2
    car.negacc = 3
    carbox2 = init_cars_distributed(length=length, carTemplateBox=[car], lanes=lanes)
    rd2 = ExecRoad(carbox=carbox2, length=length, vmax=vmax)    # 有初始车辆的道路

.. note::
    如果想让道路上有多种车型，只需提前定义好车辆模板，然后加入carTemplateBox中，提供它们的pers(比例)即可(pers之和必须为1.0)，如::

        carbox = init_cars_distributed(length=length, carTemplateBox=[car1, car2], pers=[0.7, 0.3], lanes=lanes)

开始仿真
^^^^^^^^

得到初始好的道路后，设定运行规则便可以进行仿真了

设rd为一条初始化完毕的道路，使用NaSch规则仿真 100s::

    ...
    exectime = 100
    rd.set_exec_rule('NS')
    for t in xrange(exectime):
        rd.reflush_status()

::

    ExecRoad.reflush_status() 
    
------ 刷新道路上所有车辆的状态，timestep为1s

.. attention:: 
    运行规则一定要记得设定，如果不设定的话默认值为 NS

    Key的可选值为 
 
 * NS 
 * CD 
 * MCD 
 * KKW

可以用 *print rd* 来获取道路的当前信息。输出的一个例子::

 +===================+
 - 运行规则及道路HashValue：<bound method ExecRoad.NS of <road.ExecRoad object at 0x7f108147e5d0>>
 - 车道数:3 - 道路长度(m):2000 - 运行时间(s):0 - 是否为入口:False - 是否为出口:False
 --------------------
 - 车道_0 - 车辆数目:12 - 平均车速：14.167 - 已通过车辆数：0
 - 车道_1 - 车辆数目:12 - 平均车速：15.833 - 已通过车辆数：0
 - 车道_2 - 车辆数目:12 - 平均车速：14.167 - 已通过车辆数：0
 -  整体  - 车辆数目:36 - 平均车速：14.722 - 已通过车辆数：0
 --------------------
 - 连接道路：None - 时间边界条件：False - 循环边界条件：False
 +===================+

道路自身也有许多方法获取当前的信息，下面介绍几个常用的：

::

    ExecRoad.get_cars_locate() 

------ 可以得到目前时刻车辆的位置信息，返回值的形式为 **list** 中嵌套 **numpy.array** 

::

    ExecRoad.get_cars_v()      

------ 可以得到目前时刻车辆的速度信息，返回值的形式为 **list** 中嵌套 **numpy.array** 

::

    ExecRoad.get_mean_speed()  

------ 可以得到目前时刻各车道的平均速度和整体的平均速度，第一个返回值的形式为为 **numpy.array** ,第二个返回值的形式为 **float** 

一个简单的例子::

    ...
    lane_v, whole = ExecRoad.get_mean_speed()

.. attention::

    当车道上没有车时，车道的平均速度被 **-1** 所标记。当所有车道上都无车时，整体平均速度为 **None**


当然，也可以直接得到整个carbox，从而直接得到车辆操纵权::

    ExecRoad.get_cars()

.. warning::

    事实上，在没有特殊的要求时，十分不推荐直接从外部影响车辆的状态。但是可能本库在某些方面并不能满足您的需求，所以还是开放了车辆对象的直接获取。希望您在做出行动时一定要清楚自己在干什么。
    （更推荐研究reflush_status这个方法后，直接在源码上进行扩充或修改。）

车辆自动循环
^^^^^^^^^^^^^^^

一般只有初始的车辆是不够的，大多都需要持续观察道路一定时间。所以在仿真过程中需要持续的添加车辆。

如果您阅读了之前的数学模型中的通用规则，就会知道这里提供两种边界更新方式，具体的规则前面有提到过，这里不再赘述。


循环边界条件
"""""""""""""

::

    ExecRoad.cycle_boundary_condition(switch, carTemplateBox, pers=None)

循环边界相对简单，*switch* 为开关，设定为True便开启了，*carTemplateBox* 与 *pers* 的定义同前面的默认初始化函数


时间边界条件
"""""""""""""

::

    ExecRoad.time_boundary_condition(switch, carTemplateBox, pers=None, timeStep=1, nums=1)

------ *timeStep* 添加车辆的时间间隔，必须为整数

------ *nums* 添加时添加的车辆数目 

.. note::

    - 无论是哪种边界条件，都不需要给模板设置车道号
    - 更新时，如果道路入口处没有车身长度的空位时，不会添加车辆，使用循环边界条件时请特别注意这一点

道路连接
^^^^^^^^^^

道路之间可以通过::

    ExecRoad.set_connect_to(road, insertpostion=0.0)

来连接，以一条道路的末尾连接制定道路的指定位置（默认为入口）

统计
------
