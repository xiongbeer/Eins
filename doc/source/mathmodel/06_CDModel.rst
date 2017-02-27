Comfortable-driving(CD) 舒适驾驶模型
====================================
.. [Ref] W. Knospe, L. Santen and A. Schadschneider et al. Towards a realistic microscopic description of highway traffic. J. Phys. A 33, L477~L485 (2000)

数学定义
^^^^^^^^

.. note::
    由于在该模型中引入了刹车灯的效应，所以又称为刹车灯模型(breaking light,BL)

在CD模型中，引入了随机慢化函数：

    if (b\ :sub:`n+1`\  and  t\ :sub:`h`\ < t\ :sub:`s`\ )  then
        p(v\ :sub:`n`\ (t), b\ :sub:`n+1`\ (t), t\ :sub:`h`\ , t\ :sub:`s`\) = p\ :sub:`b`\
    elif  (v\ :sub:`n`\  ==  0 )  then
        p(v\ :sub:`n`\ (t), b\ :sub:`n+1`\ (t), t\ :sub:`h`\ , t\ :sub:`s`\) = p\ :sub:`0`\
    else
        p(v\ :sub:`n`\ (t), b\ :sub:`n+1`\ (t), t\ :sub:`h`\ , t\ :sub:`s`\) = p\ :sub:`d`\                                  

和有效距离：

     d\ :sub:`n`\ \ :sup:`eff` = d\ :sub:`n`\ + max(v\ :sub:`anti`\ - gap\ :sub:`safety`\  , 0)

其中b\ :sub:`n`\是车辆n的刹车灯状态，b\ :sub:`n`\ = 1(0) 表示刹车灯亮（灭）。t\ :sub:`h`\ = d\ :sub:`n`\ / v\ :sub:`n`\ (t) 是车辆的时间车头距，t\ :sub:`s`\ = min(v\ :sub:`n`\ (t), h)为安全车间间距，h用来确定刹车灯的影响范围。v\ :sub:`anti`\ = min(d\ :sub:`n+1`\ , v\ :sub:`n+1`\ )是前车的期望速度，gap\ :sub:`safety`\ 是控制参数。演化规则如下：

    #. 确定随机慢化概率： p =  p(v\ :sub:`n`\ (t), b\ :sub:`n+1`\ (t), t\ :sub:`h`\ , t\ :sub:`s`\)
    #. 加速：
        if [ (b\ :sub:`n+1`\ (t) == 0  and  b\ :sub:`n`\ (t)  ==  0) or t\ :sub:`h`\ >= t\ :sub:`s`\]  then
            v\ :sub:`n`\ (t+1) = min(v\ :sub:`n`\ (t) + 1, v\ :sub:`max`\ )
        else
            v\ :sub:`n`\ (t+1) = v\ :sub:`n`\ (t)
    #. 减速：
        v\ :sub:`n`\ (t+1) = min(d\ :sub:`n`\ \ :sup:`eff` , v\ :sub:`n`\ (t+1))
        if (v\ :sub:`n`\ < v\ :sub:`n`\ (t))  then
            b\ :sub:`n`\ (t+1) = 1
    #. 慢化：
        if (rand() < p) then
            v\ :sub:`n`\ (t+1) = max(v\ :sub:`n`\ (t+1)-1, 0)

            if (p == p\ :sub:`b`\ )  then
                b\ :sub:`n`\ (t+1) = 1 
    #. 位置更新： x\ :sub:`n`\ (t+1) = x\ :sub:`n`\ (t) + v\ :sub:`n`\ (t+1)
这里rand()是0~1之间均匀分布的随机数。
