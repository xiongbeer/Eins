BJH 慢启动规则
==============
.. [Ref] S. C. Benjamin, N. F. Johnson and P. M. Hui. Cellular automaton models of traffic flow along a highway containing a junction. J. Phys. A 29, 3119~3127 (1996)

数学定义
^^^^^^^^
此规则也是通过引入慢启动规则对NS模型进行修正，但是其慢启动规则不同于TT规则，其演化规则如下：
    
    #. 加速：v\ :sub:`n`\ -> min(v\ :sub:`n`\+1, v\ :sub:`max`\)
    #. 慢启动规则：如果flag eq 1，则以概率p\ :sub:`s`\，v\ :sub:`n`\ -> 0
    #. 减速：v\ :sub:`n`\ -> min(v\ :sub:`n`\, d\ :sub:`n`\)
    #. 随机慢化：以概率p，Vn -> max(v\ :sub:`n`\-1, 0)
    #. 运动：x\ :sub:`n`\ -> x\ :sub:`n`\ + v\ :sub:`n`\

这里，flag是一个标示，用来区分一辆车是采用慢启动规则(flag=1)，还是不采用(flag=0)。

.. note::
    实际上是依赖车辆的 '记忆效应' 的 '时间' 规则