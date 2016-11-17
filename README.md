***
![](./Source/logo-main.png)
# Veins - Simulations of Traffic System Based on the Theory of Cellular Automaton
***


## 项目介绍
* 道路交通流理论模型大体可分为三大类:宏观,中观,微观.  
元胞自动机属于微观模型,是集中于单个车辆在相互作用下的个体行为描述.  
主要用于研究高速公路与交通和城市网络交通.
* 该项目旨在提供一个简易上手且功能丰富的元胞自动机交通模拟库


## 开发进度  
### 绘图功能   
![](./Source/T.png) &nbsp; 时空图  
 ***
* A Ns Model Eg:
![](./Source/demo2.jpg)

 ***  

![](./Source/F.png) &nbsp;动态仿真


### 支持的模型
#### 已完成
![](./Source/T.png) &nbsp; &nbsp; 标准化周期性边界条件&开口边界性条件  
![](./Source/T.png) &nbsp; &nbsp; NS模型   
![](./Source/T.png) &nbsp; &nbsp; Takayasu-Takayasu(TT)慢启动规则   
![](./Source/T.png) &nbsp; &nbsp; BJH慢启动规则  
![](./Source/T.png) &nbsp; &nbsp; VDR慢启动规则  
![](./Source/T.png) &nbsp; &nbsp; 改进舒适驾驶(MCD)模型  
![](./Source/T.png) &nbsp; &nbsp; 舒适驾驶(CD)模型  
![](./Source/T.png) &nbsp; &nbsp; 速度效应(VE)  
#### 测试中
![](./Source/p.png) &nbsp; &nbsp; KKW模型
#### 待开发
* Lee的考虑减速限制的模型
* 双车道模型
* 多车道模型
* 双向交通模型
* BCA模型
* EBCA模型
* EBCA2模型
* GBCA模型
* CCA模型  

### 运行速度优化
![](./Source/F.png) &nbsp; &nbsp; Pypy支持  
![](./Source/F.png) &nbsp;  &nbsp; Cpython支持  
![](./Source/F.png) &nbsp;  &nbsp; Hadoop支持  

<a name="安装"></a>
## 安装
### 依赖
* python 2.7
* matplotlib
* pandas
* numpy

### 安装
目前只能clone  
后续会推送到PyPi上  

### 文档与教程
[Veins-Docs](https://veinsdocs.readthedocs.io/en/latest/index.html)
