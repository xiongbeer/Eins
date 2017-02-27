Velocity-effect(VE) 速度效应
============================
.. [Ref] X. B. Li, Q. S. Wu and R. Jiang. Cellular automaton model considering the velocity effect of a car on the successive car. Phys. Rev. E 64, 066128 (2001)

数学定义
^^^^^^^^
以外的绝大多数元胞自动机模型中，有一个共同特征，在从 t->t+1 的时间步中，车辆速度更新规则只考虑了t时刻两车的距离，而没有记入前车运动的影响，即都把前车作为静止的粒子处理。由此造成模拟速度小于实际车辆速度。

规则将减速步改为:
    v\ :sub:`n`\ -> min(v\ :sub:`n`\+1, d\ :sub:`n`\ + v\ :sup:`'` \ :sub:`n+1`\ )
    
    v\ :sup:`'` \ :sub:`n+1`\ = min(v\ :sub:`max`\-1, v\ :sub:`n+1`\, max(0, d\ :sub:`n+1`\ -1))
其中v\ :sup:`'` \ :sub:`n+1`\是n+1车在 t->t+1 时间步里的虚拟速度。它由NS模型演化规则所能得到的最小可能速度。一方面考虑了前车的速度效应，另一方面又确保在模型的更新过程中不会发生撞车。