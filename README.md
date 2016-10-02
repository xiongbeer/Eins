# Improved-Nagel-Schreckenberg-Traffic-Simulation/NS模型交通仿真


## 目录
* [项目介绍](#项目介绍)  
* [使用向导](#使用向导)  
* [算法原理](#算法原理)  

<a name="项目介绍"></a>
## 项目介绍
项目的设计想法来自2016年CUMCM(全国大学生数学建模竞赛)中的B题,关于交通仿真的.
大型交通仿真软件庞大而难学,所以想开发一个可视化、简单易学和通用性强的小型仿真软件,针对人群是有部分编程基础的人。
目前用的算法只有元胞自动机(改进的),后续应该会增加算法。

正在寻找英文翻译合作者...

<a name="使用向导"></a>
##使用向导
目前整体分为三大部分:   
1.道路模块  
2.绘图模块  
3.统计模块  
###道路模块
> **Car**() --结构体 --> 用于构造运行的车辆  
>> **Parameters**:   
    **name(default = True)**:				车的名称(类别),可帮助细化统计分类.  
    **length(default = True)**:				车的长度,是决定车距的参数之一.  
    **vDistance(default = True)**:			真实最小车距,是决定车距的参数之一.  
    **v(default = True)**:					当前速度.  
    **view(default = True)**:				车的视野距离,影响随机减速因子.  
    **locate(default = True)**:				车在道路上的原始一维坐标.  
    **height(default = True)**:				车的高度.  
    **acc(default = True)**:				车的加速度.  
    **negacc(default = True)**:				车的减速度(非最大减速).  

> **Road**(object) --基类 -->  
>> **Parameters**:  
    **self.carBox(default = False) = carBox_**:				道路上所有车辆及其具体状态和参数  
    **self.enterCars(default = False) = enterCars_**:		进入此路的车辆数  
    **self.vmax(default = False) = vmax_**:					道路最大车速  
    **self.length(default = False) = length_**:				道路长度  
    **self.target(default = True) = target_**:				追加长度,一般取0就可以了  
    **self.lanes(default = True) = lanes_**:				车道数,默认为单车道  
    **self.laneFlag(default = True) = 0**:					标记当前操作的车道号  
    **self.endCars(default = True) = np.array([])**:		list的长度表示有多少车辆需要进入其他道路,键值为其速度  
    **self.enterFlag(default = True) = enterFlag_**:		标记此道是否是入口,如果非入口,初始化车辆必须要有一个哨兵车辆(v = -1.0 locate = 0.0)   
    **self.alpha(default = True) = alpha_**:				减速概率的alpha因子,不能随意修改,除非你知道自己在干什么  
    **self.beta(default = True) = beta_**:					减速概率的beta因子,同上  
    **self.autoAdderSwitch(default = True) = False**:		是否自动添加车辆  
    **self.autoAdderByTime(default = True) = False**:		是否按时间自动添加车辆,与前一个Flag冲突  
    **self.autoAdder(default = False) = None**:				自动添加车辆的初始速度  
    **self.connectRoad(default = True) = connectRoad_**:	连接的公路(入口),默认值为空  
    **self.autoAddTime(default = True) = 0**:				用户定义的自动添加车辆的时间间隔  
    **self.timeCounter(default = True) = 0**:				系统内部用于自动添加车辆的时间计数器  
    **self.wholeTime(default = True) = 0**:					总的运行时间  
	**self.leaveCars(default = True) = [0]*lanes_**:		离开此路的车辆数  
>> **func**:  
	--待更新  

<a name="算法原理"></a>
##算法原理
###Nagel–Schreckenberg model && 元胞自动机
####基本思想  
>在纳格尔–元模型中道路被划分为细胞(点格阵).在原有的模型中，这些细胞是单排的两端连接,所有的细胞组成一个圆排列(周期性边界条件).每个细胞都是**空的**道路或包含一个**单一**的汽车.每辆车都分配一个速度是0和最大速度之间的整数（在Nagel–Schreckenberg model原作品中,max=5）  
以下这四个动作重复多次,是一个学习过程,可以形成任何交通堵塞。模型就是一个例子元胞自动机。该模型是一个单车道,没有超车
算法基本工作流程:  
    ( **1** 在这里指一个细胞单位)  
    * 当前速度是 v   
    * 如果前面没车，它在下一秒的速度会提高到 v + 1 ，直到达到规定的最高限速  
    * 如果前面有车，距离为d，且 d < v.那么它在下一秒的速度会降低到 d - 1   
    * 此外，司机还会以概率 p(定值) 随机减速， 将下一秒的速度降低到 v - 1  

* 改模型说明了即使没有任何外在原因,道路也可能发生拥堵
* 该模型是简约的,即该模型定义的任何元素的缺失会立即导致交通仿真的关键性能损失。
* 利用并行计算机模拟以该模型为基础的数百万辆汽车是可能的(运用实例:北莱茵-威斯特法伦州的脱机模拟交通预测系统(德国))

以上参考来源于wiki

####模型改进
原模型有个很大的缺陷,就是司机的减速概率是**定值随机的**  
在实际生活中,司机无缘无故的减速概率并不会很高,应该说非常**低**  
这里采用**动态减速概率**,基于司机的**视野距离内车的数目**和**当前自身车速**  
视野范围、最大速度、当前测速、两个指数参数分别为: <img src="http://www.forkosh.com/mathtex.cgi?\delta.V_{max}.v_i.\alpha.\beta.">  
计算公式为:  
*随机减速概率*:  
<img src="http://www.forkosh.com/mathtex.cgi?\rho_l^\alpha(v_i(t)/V_{max})^\beta">  
其中*局部密度*:  
<img src="http://www.forkosh.com/mathtex.cgi?\rho_l=1/\delta(\sum_{r=i+1}^{i+\delta})\eta(r)">   
<img src="http://www.forkosh.com/mathtex.cgi?\eta(r)">
为布尔量,有车占据此细胞则为1,否则为0  
两个**指数参数**的值需要使用者自己给定(可以依据公路实际数据或者化为最优化问题来解得)  

参考论文: ZHU Liu-hua,KONG Ling-jiang,LIU Mu-ren. Investigation of an Improved Nagel-Schreckenberg Traffic Flow Model ,China Guangxi Sciences 2007,14(3):253~256
