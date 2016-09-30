#!/usr/bin/env python
# coding=utf-8

#优化工作: 0%
#GUI: 0%

import numpy as np

locateEmpty = np.array([-1])
vBoxEmpty   = np.array([0])

class Road(object):
    'Road && Cars'

    def __init__(self, locate_, vBox_, vmax_, length_, view_ = 80, voffset_ = 2.7, negvoffset_ = 1.2,
                target_ = 0.0, lanes_ = 1, enterCars_ = 0, leaverCars_ = 0, alpha_ = 0.6,
                 beta_ = 0.2, frames_ = 1, enterFlag_ = False, connectRoad_ = None):
        self.enterCars = enterCars_             #进入此路的车辆数
        self.leaverCars = leaverCars_           #离开此路的车辆数
        self.locate = locate_                   #各个车在此路的位置
        self.vBox = vBox_                       #各个车的车速
        self.view = view_                       #道路视距
        self.vmax = vmax_                       #道路最大车速
        self.length = length_                   #道路长度
        self.target = target_                   #追加长度,一般取0就可以了
        self.lanes = lanes_                     #车道数,默认为单车道
        self.laneFlag = 0                       #标记当前操作的车道号
        self.endCarsV = np.array([])            #list的长度表示有多少车辆需要进入其他道路,键值为其速度
        self.meanV = np.array([])               #车道的平均速度
        self.enterFlag = enterFlag_             #标记此道是否是入口,如果非入口,
                                                #locate初始化值必须为[np.array([-1.0])],vBox必须为[np.array([0])](单车道,
                                                #多车道只需向list多添加初始值就可以了)

        self.alpha = alpha_                     #减速概率的alpha因子,不能随意修改,除非你知道自己在干什么
        self.beta = beta_                       #减速概率的beta因子,同上
        self.voffset = voffset_/frames_                  #基于帧数和加速度的位移,frames_为帧数
        self.negvoffset = negvoffset_/frames_            #基于帧数和减速度的位移(非最大紧急减速度,请根据实际情况调整)
        self.frames = frames_
        self.autoAdderSwitch = False            #是否自动添加车辆
        self.autoAdderByTime = False            #是否按时间自动添加车辆,与前一个Flag冲突
        self.autoAdderV = 0                     #自动添加车辆的初始速度
        self.connectRoad = connectRoad_         #连接的公路(入口),默认值为空
        self.autoAddTime = 0                    #用户定义的自动添加车辆的时间间隔
        self.timeCounter = 0                    #系统内部用于自动添加车辆的时间计数器
        self.wholeTime = 0                      #总的运行时间
    #标记线内的函数由用户根据情况自行使用
    #-----------------------------------------------------
    def getCarsV(self):
        return self.vBox
    def getCarsLocate(self):
        return self.locate
    def getRoadLanes(self):
        return self.lanes
    def getEndCarsNum(self):
        return self.endCarsV.size
    def getRoadLength(self):
        return self.length+self.target
    def getRoadVMax(self):
        return self.vmax
    #减少需要进入其他道路车辆的计数,并且返回那辆车的速度
    def reduceEndCars(self):
        v = self.endCarsV[0]
        self.endCarsV = np.delete(self.endCarsV, 0)
        return v

    #更新道路状态(即将车t时刻的状态更新到时刻t+1)
    def reflushStatus(self):
        currentV = 0.0      #用于统计当前道路平均车速
        laneVCounter = 0
        self.timer()
        #每个车道分别计算,也就是车不会中途改变车道
        for lane in xrange(0,self.lanes):
            slowVic = np.random.random(self.locate[lane].size)
            if self.locate[lane].size >= 2:
                for i in xrange(0,self.locate[lane].size - 1):

                    #获得视野距离内前方车辆的数目
                    temp = self.locate[lane][i] + self.view - self.locate[lane][i:]
                    temp = temp[temp >= 0]
                    carsNum = temp.size

                    #计算减速概率
                    p = self.pCounter(float(carsNum), float(self.vBox[lane][i]), self.view, self.vmax)
                    distance = self.locate[lane][i+1] - self.locate[lane][i]                #汽车与前面汽车的距离
                    if self.locate[lane][i] != -1.0:
                        self.vBox[lane][i] = self.getV(self.vBox[lane][i], distance, self.vmax, p,
                        self.voffset, self.negvoffset, slowVic[i])

                        self.locate[lane][i] += self.vBox[lane][i]

            #最前的车单独计算
            if self.locate[lane].size > 0 and self.locate[lane][-1] != -1.0:
                self.vBox[lane][-1] = self.getV(self.vBox[lane][-1], self.length,self.vmax, 0,
                self.voffset, self.negvoffset, np.random.random(1)[0])
                self.locate[lane][-1] += self.vBox[lane][-1]
                if self.locate[lane].size > 1 and self.enterFlag == False:
                    currentV += self.vBox[lane][1:].mean()
                    laneVCounter += 1
                else:
                    currentV += self.vBox[lane].mean()
                    laneVCounter += 1
                #到达尽头后移除车辆,增加endCarsV的值，代表有车需要进入其他道路
                if self.locate[lane][-1] >= self.length + self.target:
                    leaveV = self.vBox[lane][-1]
                    self.endCarsV = np.append(self.endCarsV, self.vBox[lane][-1])
                    self.vBox[lane] = np.delete(self.vBox[lane], -1)
                    self.locate[lane] = np.delete(self.locate[lane], -1)
                    self.leaverCars += 1
                    #如果出口连接了其他的道路,则自动将离开的车加入其入口
                    if self.connectRoad != None:
                        self.connectRoad.addCar(leaveV)
                        self.leaverCars -= 1

                    #如果需要自动添加车辆,每离开一辆车就自动在起始初添加一辆车(一般用于入口)
                    if self.autoAdderSwitch == True:
                        self.addCar(self.autoAdderV)
        
        #如果有需要,按时间添加车辆的LOOP
        if self.autoAdderByTime == True:
            if self.autoAddTime == self.timer(get = True):
                self.timer(reset = True)
                self.addCar(self.autoAdderV)
        #如果有车就统计平均车速
        if laneVCounter != 0:
            self.meanV = np.append(self.meanV, [currentV/laneVCounter])

    #道路增加一辆车
    def addCar(self, v, position = 0.0):
        insertIndex = 0             #插入位置
        #增加新的车辆，每个车道分到车的概率相等
        self.enterCars += 1
        if self.laneFlag < self.lanes - 1:
            self.laneFlag += 1
        else:
            self.laneFlag = 0

        for l in self.locate[self.laneFlag]:
            if position > l:
                insertIndex += 1
            else:
                break

        self.locate[self.laneFlag] = np.insert(self.locate[self.laneFlag], insertIndex, position)
        self.vBox[self.laneFlag] = np.insert(self.vBox[self.laneFlag],insertIndex,v)

    #清空离开道路车辆数的计数
    def reLeave(self):
        self.leaverCars = 0
    
    #自动添加车辆(每离开一辆就添加一辆)
    def evenAddAutomaticVehicleSwitch(self, switch, v):
        if self.autoAdderByTime != True:
            self.autoAdderSwitch = switch
            self.autoAdderV = v
        else:
            print 'Set add car automatic failed,there alreadly existed another mode'

    #按时间间隔添加车辆,与前一个冲突
    def addCarAutomaticByTime(self, switch, v, timeStep):
        if self.autoAdderSwitch != True:
            self.autoAdderByTime = switch
            self.autoAdderV = v
            if timeStep != 0:
                self.autoAddTime = timeStep
            else:
                print 'timeStep cannot be zero'
        else:
            print 'Set add car automatic by time failed,there alreadly existed another mode'
    def setConnectTo(self, road):
        self.connectRoad = road
    #---------------------------------------------------
    def timer(self, get = False,reset = False):
        self.wholeTime += 1
        if get == True:
            return self.timeCounter
        if reset == True:
            self.timeCounter = 0
        else:
            self.timeCounter += 1
    #计算实时随机减速概率
    def pCounter(self, carsNum, v, dview, vmax):
        A = (carsNum/dview)**self.alpha
        B = (v/vmax)**self.beta
        return A*B

    #计算车辆当前速度
    def getV(self, v, distance, vmax, p, voffset, negvoffset, slowVic):
        if v <= distance:
            if slowVic < p:
                if v - negvoffset > 0:
                    v -= negvoffset

                else:
                    v = 0
            else:
                if v + voffset < vmax:
                    v += voffset
                else:
                    v = vmax
        else:
            if v > 0 and distance - negvoffset > 0:
                v = distance - negvoffset
            else:
                v = 0
        return v/self.frames


#在指定长度上初始化指定数量的车辆,可以指定分布,默认线性均匀分布
def initCarsDistributed(length, carsNum, initV, distributed = 'linear'):
    if distributed == 'linear':
        cars = np.array(sorted(np.random.random(carsNum)*length))
        v = np.array([initV]*cars.size)
        return cars, v
    else:
        print 'No such distributed'
