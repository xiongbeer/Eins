Velocity-dependent-randomization(VDR) 慢启动规则
================================================
.. [Ref] R. Barlovic, L. Santen and A. Schreckenburg. Metastable states in cellular automata for traffic flow. Eur. Phys. J. B 5, 793~800 (1998)

数学定义
^^^^^^^^
此规则也是通过引入慢启动规则对NS模型进行修正，但是其慢启动规则不同于TT和BJH规则，其演化规则如下：

    1. 确定随机慢化概率:

        if (v == 0) then
            p(v) = p\ :sub:`0`\
        else
            p(v) = p
    
    2. 加速：v\ :sub:`n`\ -> min(v\ :sub:`n`\+1, v\ :sub:`max`\)
    3. 减速：v\ :sub:`n`\ -> min(v\ :sub:`n`\, d\ :sub:`n`\)
    4. 随机慢化：如果 flag eq 1，那么以概率p0有 v\ :sub:`n`\ -> max(v\ :sub:`n`\-1, 0);如果 flag eq 0，那么以概率p有 v\ :sub:`n`\ -> max(v\ :sub:`n`\-1, 0)
    5. 运动： x\ :sub:`n`\ -> x\ :sub:`n`\ + v\ :sub:`n`\

.. note::
    随机慢化概率不再是固定不变的，而是车辆速度的函数 p=p(v)