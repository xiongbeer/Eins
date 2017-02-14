Takayasu-Takayasu(TT) 慢启动规则
================================
.. [Ref] M. Takayasu and H. Takayasu. 1/f noise in a traffic model. Fractals 1, 860~866 (1993)

数学定义
^^^^^^^^
在这一模型中，如果一辆静止车辆前面恰好只有一个空元胞，那么该车以概率 q\ :sub:`t`\=1-p\ :sub:`t`\ 加速，而对其他所有情况， 车辆均按确定性规则进行加速。其他更新过程均和NS模型中的 step2 ~ step4 是完全一致的。 

.. note::
    实际上是依赖车辆前方空元胞数的 '空间' 规则