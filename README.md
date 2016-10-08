# Improved-Nagel-Schreckenberg-Traffic-Simulation/NS模型交通仿真
# 代码结构将有大的调整,目前重心放在算法的扩充上,后期可视化预计用PyOpenGL/VisPy + PyQt4来构建.

## TODOLIST
** 下一次pus可能要比较久之后了,届时发布为Stable,敬请期待 **
* 标准化周期性边界条件&开口边界性条件
* 最原始的NS模型
* Takayasu-Takayasu(TT)慢启动规则
* BJH慢启动规则
* VDR慢启动规则
* 速度效应模型
* 舒适驾驶(CD)模型
* 改进舒适驾驶(MCD)模型
* 同步流
* KKW模型
* Lee的考虑减速限制的模型
* 鸣笛效应
* 双车道模型
* 多车道模型
* 双向交通模型
* BCA模型
* EBCA模型
* EBCA2模型
* GBCA模型
* CCA模型

## 目录
* [项目介绍](#项目介绍)  
* [例子](#例子)
* [安装](#安装)
* [使用向导](#使用向导)  
* [算法原理](#算法原理)  

<a name="项目介绍"></a>
## 项目介绍
项目的设计想法来自2016年CUMCM(全国大学生数学建模竞赛)中的B题,关于交通仿真的.
大型交通仿真软件庞大而难学,所以想开发一个可视化、简单易学和通用性强的小型仿真软件,针对人群是有部分编程基础的人。
目前用的算法只有元胞自动机(改进的),后续应该会增加算法。

正在寻找英文翻译合作者...
<a name="例子"></a>
## 例子
### exp-1
定义两条道路:   
入口道路rd  
* 长度为1000m
* 车道数量为2
* 最大限速60km/h
* 初始时均匀放置100辆初速度为30km/h的小型汽车(每条车道都是100)
* 边界条件为每离开一辆车就自动添加一辆新的相同初始条件的车

出口道路rd2:  
* 长度为500m
* 车道数量为2
* 最大限速为60km/h
* 初始时道路是空的

测试源代码:
```
#!/usr/bin/env python
# coding=utf-8
import numpy as np
import basicroad as br	#导入道路模块
import basicplot as bp	#导入绘图模块
carsNum = 100			 #初始车的数量
vmax = 16.7			   #道路的限速(m/s)
carTemp = br.Car()		#边界条件添加的车辆信息
carTemp.v = vmax * 0.5

#获得初始化的车辆分布信息
InitCar = br.initCarsDistributed(1000, carTemp, [vmax * 0.5] * carsNum, carsNum, lanes=2)

if __name__ == '__main__':
	#定义并初始化两条道路
	rd = br.Road(InitCar, vmax, 1000, enterFlag_=True,lanes_=2)
	rd2 = br.Road(br.initEmptyRoad(2), vmax, 500, lanes_=2)
	#将rd与rd2连接起来(rd的出口连向rd2的入口)
	rd.setConnectTo(rd2)
	#打开rd的边界条件
	rd.addCarAutomaticByTime(True, carTemp, 2)
	#导入要绘制的道路
	bp.addRoad(np.array([0, 50]), np.array([50, 50]), rd)
	bp.addRoad(np.array([60, 90]), np.array([50, 50]), rd2)
	#开始动态绘图
	bp.plot()

```

#### 运行结果
最初的状态:
![exp2](/Source/exp_2.png)
可以看到图中由3种颜色分布:  
* 红: 0 <= v <= vmax*0.2
* 黄: vmax*0.2 < v <= vmax*0.6
* 绿: v > vmax*0.6

也就是说,红色和黄色的聚集地代表了道路不通畅的地方,绿色代表了车辆流畅通行  

![exp](/Source/exp.png)
运行一段时间后,道路变为了全绿通行状态,这时说明道路可以平稳运行了.   

<a name="安装"></a>
## 安装
### 依赖
* python 2.7
* matplotlib
* pandas
* numpy

### 安装
目前只能clone  
后续会推送道PyPi上  

<a name="使用向导"></a>
## 使用向导
目前整体分为三大部分:   
1.道路模块  
2.绘图模块  
3.统计模块  
### 道路模块
> **Car**() --结构体 --> 用于构造运行的车辆  

|**Parameters**:|**说明**|
| :-------: | :--------- |
|    **name(default = True)**|				车的名称(类别),可帮助细化统计分类|
|    **length(default = True)**|				车的长度,是决定车距的参数之一|
|    **vDistance(default = True)**|			真实最小车距,是决定车距的参数之一|
|    **v(default = True)**|					当前速度|
|    **view(default = True)**|				车的视野距离,影响随机减速因子|
|    **locate(default = True)**|				车在道路上的原始一维坐标|
|    **height(default = True)**|				车的高度|
|    **acc(default = True)**|				车的加速度|
|    **negacc(default = True)**|				车的减速度(非最大减速)|

> **Road**(object) --基类 -->  

|**Parameters**:|**说明**|
| :-------: | :--------- |
|    **carBox_(default = False)**|				道路上所有车辆及其具体状态和参数|
|    **vmax_(default = False)**|				道路最大车速|
|    **length_(default = False)**|			道路长度|
|    **target_(default = True)**|			追加长度,一般取0|
|    **lanes_(default = True)**|			车道数,默认为单车道|
|    **enterFlag_(default = True)**|	标记此道是否是入口|
---
>> **func**:  
	--待更新  

<a name="算法原理"></a>
## 算法原理
### Nagel–Schreckenberg model && 元胞自动机
#### 基本思想  
>在纳格尔–元模型中道路被划分为细胞(点格阵).在原有的模型中，这些细胞是单排的两端连接,所有的细胞组成一个圆排列(周期性边界条件).每个细胞都是**空的**道路或包含一个**单一**的汽车.每辆车都分配一个速度是0和最大速度之间的整数（在Nagel–Schreckenberg model原作品中,max=5）  
以下这四个动作重复多次,是一个学习过程,可以形成任何交通堵塞。模型就是一个例子元胞自动机。该模型是一个单车道,没有超车  
算法基本工作流程:  
    ( **1** 在这里指一个细胞单位)  
    1. 当前速度是 v   
    2. 如果前面没车，它在下一秒的速度会提高到 v + 1 ，直到达到规定的最高限速  
    3. 如果前面有车，距离为d，且 d < v.那么它在下一秒的速度会降低到 d - 1   
    4. 此外，司机还会以概率 p(定值) 随机减速， 将下一秒的速度降低到 v - 1  

* 改模型说明了即使没有任何外在原因,道路也可能发生拥堵
* 该模型是简约的,即该模型定义的任何元素的缺失会立即导致交通仿真的关键性能损失。
* 利用并行计算机模拟以该模型为基础的数百万辆汽车是可能的
> 运用实例:北莱茵-威斯特法伦州的脱机模拟交通预测系统(德国)
城市智能交通项目TRANSIMS(美国)
杜伊斯堡的内城交通
达拉斯/福斯-华斯地区的交通规划
北莱茵-魏斯特伐亚地区的交通公路网

以上参考部分来源于wiki

#### 模型改进
原模型有个很大的缺陷,就是司机的减速概率是**定值随机的**  
在实际生活中,司机无缘无故的减速概率并不会很高,应该说非常**低**  
这里采用**动态减速概率**,基于司机的**视野距离内车的数目**和**当前自身车速**  
视野范围、最大速度、当前测速、两个指数参数分别为: <img src="http://www.forkosh.com/mathtex.cgi?\delta.V_{max}.v_i.\alpha.\beta.">  
计算公式为:  
*随机减速概率*:  
> <img src="http://www.forkosh.com/mathtex.cgi?p=\rho_l^\alpha(v_i(t)/V_{max})^\beta">  
其中*局部密度*:  
> <img src="http://www.forkosh.com/mathtex.cgi?\rho_l=1/\delta(\sum_{r=i+1}^{i+\delta})\eta(r)">   
<img src="http://www.forkosh.com/mathtex.cgi?\eta(r)">
为布尔量,有车占据此细胞则为1,否则为0  
两个**指数参数**的值需要使用者自己给定(可以依据公路实际数据或者化为最优化问题来解得)  

参考论文: ZHU Liu-hua,KONG Ling-jiang,LIU Mu-ren. Investigation of an Improved Nagel-Schreckenberg Traffic Flow Model ,China Guangxi Sciences 2007,14(3):253~256
