Modified-comfortable-driving(MCD) 改进的舒适驾驶模型
====================================================
.. [Ref] R. Jiang and Q. S. Wu. Cellular automata models for synchronized traffic flow. J. Phys. A theory. J. Phys. A 36, 381~390 (2003)

数学定义
^^^^^^^^
    慢启动规则的引入是为了描述驾驶员的不敏感的反应。一般认为静止车辆驾驶员没有运动车辆驾驶员敏感，因此静止车辆的慢化概率较大。然而，在这个模型中认为：刚停下的车辆的驾驶员仍十分敏感，只有停止时间超过一定时间 t\ :sub:`c`\ ，驾驶员才会变得不那么敏感。
在MCD模型中，随机慢化函数为：    
    if (b\ :sub:`n+1`\  and  t\ :sub:`h`\ < t\ :sub:`s`\ )  then
        p(v\ :sub:`n`\ (t), b\ :sub:`n+1`\ (t), t\ :sub:`h`\ , t\ :sub:`s`\) = p\ :sub:`b`\
    elif  (v\ :sub:`n`\  ==  0 and t\ :sub:`st`\ >= t\ :sub:`c`\)  then
        p(v\ :sub:`n`\ (t), b\ :sub:`n+1`\ (t), t\ :sub:`h`\ , t\ :sub:`s`\) = p\ :sub:`0`\
    else
        p(v\ :sub:`n`\ (t), b\ :sub:`n+1`\ (t), t\ :sub:`h`\ , t\ :sub:`s`\) = p\ :sub:`d`\ 
   
演化规则为：
    #. 确定随机慢化概率： p =  p(v\ :sub:`n`\ (t), b\ :sub:`n+1`\ (t), t\ :sub:`h`\ , t\ :sub:`s`\)
    #. 加速：
        if [(b\ :sub:`n+1`\ (t) == 0 or t\ :sub:`h`\ >= t\ :sub:`s`\ ) and v\ :sub:`n`\ (t) > 0]  then
            v\ :sub:`n`\ (t+1) = min(v\ :sub:`n`\ (t) + 2, v\ :sub:`max`\ )
        elif (v\ :sub:`n`\ (t) == 0)  then
            v\ :sub:`n`\ (t+1) = min(v\ :sub:`n`\ (t) + 1, v\ :sub:`max`\ )
        else
            v\ :sub:`n`\ (t+1) = v\ :sub:`n`\ (t)
    #. 减速：v\ :sub:`n`\ (t+1) = min(d\ :sub:`n`\ \ :sup:`eff` , v\ :sub:`n`\ (t+1))
    #. 慢化：
        if(rand() < p)  then
            v\ :sub:`n`\ (t+1) = max(v\ :sub:`n`\ (t+1) -1, 0)
    #. 确定刹车灯状态 b\ :sub:`n+1`\ (t+1)：
        if (v\ :sub:`n`\ (t+1) < v\ :sub:`n`\ (t))  then
            b\ :sub:`n`\ (t+1) = 1
        elif(v\ :sub:`n`\ (t+1) > v\ :sub:`n`\ (t)) then
            b\ :sub:`n`\ (t+1) = 0
        else
            b\ :sub:`n`\ (t+1) = b\ :sub:`n`\ (t)
    #. 确定t\ :sub:`st`\ ：
        if (v\ :sub:`n`\ (t+1) == 0)  then
            t\ :sub:`st`\ += 1
        elif (v\ :sub:`n`\ (t+1) > 0)  then
            t\ :sub:`st`\ = 0
    #. 位置更新： x\ :sub:`n`\ (t+1) = x\ :sub:`n`\ (t) + v\ :sub:`n`\ (t+1)
