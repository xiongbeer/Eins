视野规则
========
.. [Ref] ZHU Liu-hua,KONG Ling-jiang,LIU Mu-ren Investigation of an IImproved Nagel-Schreckenberg Traffic Flow Model Guangxi Sciences 2007, 14(3):253~256

数学定义
^^^^^^^^

与VDR规则类似，视野规则也是采用动态随机慢化概率，概率受到司机的 **视野距离内车的数目** 和 **当前自身车速** 的影响。

* 视野范围、两个指数参数分别为δ,α,β 

    计算公式为:  
* 随机减速概率:  p = ρ\ :sub:`l`\ \ :sup:`α` (v\ :sub:`i`\ (t)/v\ :sub:`max`\ )\ :sup:`β`
* 其中局部密度:  ρ\ :sub:`l`\ = sum(η\ :sub:`i`\ )/δ
η\ :sub:`i`\为布尔量,有车占据此细胞则为1,否则为0 ，sum(η\ :sub:`i`\ ) 是视野内车的数量之和 

两个指数参数的值需要使用者自己给定

.. note::
    指数参数可以依据公路实际数据化为最优化问题来解得  