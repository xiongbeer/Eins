#!/usr/bin/env python
# coding=utf-8

#优化工作: 0%
#GUI: 0%

import numpy as np
import copy
Empty_L = -1
Empty_V = 0
#TODO:-逻辑BUG-道路最前的车不会考虑要进入下一条车道最后一辆车的情况
class Road(object):
    'Road && Cars'

    def __init__(self, carBox_, vmax_, length_, target_ = 0.0, lanes_ = 1,
                 enterCars_ = 0, alpha_ = 0.6, beta_ = 0.2, 
                 enterFlag_ = False, connectRoad_ = None):
        self.carBox = carBox_                   #道路上所有车辆及其具体状态和参数
        self.enterCars = enterCars_             #进入此路的车辆数
        self.leaveCars = [0]*lanes_             #离开此路的车辆数
        self.vmax = vmax_                       #道路最大车速
        self.length = length_                   #道路长度
        self.target = target_                   #追加长度,一般取0就可以了
        self.lanes = lanes_                     #车道数,默认为单车道
        self.laneFlag = 0                       #标记当前操作的车道号
        self.endCars = np.array([])             #list的长度表示有多少车辆需要进入其他道路,键值为其速度
        self.enterFlag = enterFlag_             #标记此道是否是入口,如果非入口,
                                                #locate初始化值必须为[np.array([-1.0])],vBox必须为[np.array([0])](单车道,
                                                #多车道只需向list多添加初始值就可以了)

        self.alpha = alpha_                     #减速概率的alpha因子,不能随意修改,除非你知道自己在干什么
        self.beta = beta_                       #减速概率的beta因子,同上
        self.autoAdderSwitch = False            #是否自动添加车辆
        self.autoAdderByTime = False            #是否按时间自动添加车辆,与前一个Flag冲突
        self.autoAdder = None                     #自动添加车辆的初始速度
        self.connectRoad = connectRoad_         #连接的公路(入口),默认值为空
        self.autoAddTime = 0                    #用户定义的自动添加车辆的时间间隔
        self.timeCounter = 0                    #系统内部用于自动添加车辆的时间计数器
        self.wholeTime = 0                      #总的运行时间
    def __str__(self):
        des = '\n车道数:'+str(self.lanes)+'\n道路长度:'+str(self.length+self.target)+'\n运行时间(/s):'+str(self.wholeTime)+'\n是否为入口:'+str(self.enterFlag)
        carsCounter = []
        for index, lane in enumerate(self.carBox):
            carsCounter.append(lane.size)
            des += '\n'+'车量-车道'+str(index)+':'+str(lane.size)
        des += '\n'+'车总量:'+str(sum(carsCounter))
        return des
    #标记线内的为public func
    #-----------------------------------------------------
    def getCarsLocate(self):
        output = []
        for lane in self.carBox:
            output.append(np.array([car.locate for car in lane]))
        return output
        
    def getCarsV(self):
        output = []
        for lane in self.carBox:
            output.append(np.array([car.v for car in lane]))
        return output

    def getCarsInfo(self):
        return self.carBox
    def getRoadLanes(self):
        return self.lanes
    def getEndCarsNum(self):
        return self.endCars.size
    def getRoadLength(self):
        return self.length+self.target
    def getRoadVMax(self):
        return self.vmax
    def getLeaveCars(self):
        return self.leaveCars
    #减少需要进入其他道路车辆的计数,并且返回那辆车的信息
    
    def reduceEndCars(self):
        car = self.endCars[0]
        self.endCars = np.delete(self.endCars, 0)
        return car

    #更新道路状态(即将车t时刻的状态更新到时刻t+1)
    def reflushStatus(self):
        self.timer()
        #每个车道分别计算,也就是车不会中途改变车道
        for lane in xrange(0,self.lanes):
            slowVic = np.random.random(self.carBox[lane].size)
            if self.carBox[lane].size >= 2:
                for i in xrange(0, self.carBox[lane].size - 1):

                    #获得视野距离内前方车辆的数目
                    tempLocate = np.array([])
                    for locate in self.carBox[lane][i:]:
                        tempLocate = np.append(tempLocate, locate.v)
                    temp = self.carBox[lane][i].locate + self.carBox[lane][i].view - tempLocate
                    temp = temp[temp >= 0]
                    carsNum = temp.size

                    #计算减速概率
                    p = self.pCounter(float(carsNum), self.carBox[lane][i])
                    distance = self.carBox[lane][i+1].locate - self.carBox[lane][i].locate                #汽车与前面汽车的距离
                    if self.carBox[lane][i].locate != -1.0:
                        self.carBox[lane][i].v = self.getV(self.carBox[lane][i], distance, p, slowVic[i])

                        self.carBox[lane][i].locate += self.carBox[lane][i].v
            #最前的车单独计算
            if self.carBox[lane].size > 0 and self.carBox[lane][-1].locate != -1.0:
                self.carBox[lane][-1].v = self.getV(self.carBox[lane][-1], self.length, 0, np.random.random(1)[0])
                self.carBox[lane][-1].locate += self.carBox[lane][-1].v
                #到达尽头后移除车辆,增加endCarsV的值，代表有车需要进入其他道路
                if self.carBox[lane][-1].locate >= self.length + self.target:
                    leaveCar = self.carBox[lane][-1]
                    self.endCars = np.append(self.endCars, self.carBox[lane][-1])
                    self.carBox[lane] = np.delete(self.carBox[lane], -1)
                    self.leaveCars[lane] += 1
                    #如果出口连接了其他的道路,则自动将离开的车加入其入口
                    if self.connectRoad != None:
                        self.connectRoad.addCar(leaveCar)

                    #如果需要自动添加车辆,每离开一辆车就自动在起始初添加一辆车(一般用于入口)
                    if self.autoAdderSwitch == True:
                        self.addCar(self.autoAdder)
        
        #如果有需要,按时间添加车辆的LOOP
        if self.autoAdderByTime == True:
            if self.autoAddTime == self.timer(get = True):
                self.timer(reset = True)
                self.addCar(self.autoAdder)
    
    def addCar(self, car, position = 0.0):
        car = copy.deepcopy(car)    #深复制一个对象(新建一辆车)
        insertIndex = 0             #插入位置
        #增加新的车辆，每个车道分到车的概率相等
        self.enterCars += 1
        if self.laneFlag < self.lanes - 1:
            self.laneFlag += 1
        else:
            self.laneFlag = 0

        for l in self.carBox[self.laneFlag]:
            if position > l.locate:
                insertIndex += 1
            else:
                break

        self.carBox[self.laneFlag] = np.insert(self.carBox[self.laneFlag], insertIndex, car)

    #清空离开道路车辆数的计数
    def reLeave(self):
        self.leaveCars = [0]*self.lanes
    
    #自动添加车辆(每离开一辆就添加一辆)
    def evenAddAutomaticVehicleSwitch(self, switch, car):
        if self.autoAdderByTime != True:
            self.autoAdderSwitch = switch
            self.autoAdder = car
        else:
            print 'Set add car automatic failed,there alreadly existed another mode'

    #按时间间隔添加车辆,与前一个冲突
    def addCarAutomaticByTime(self, switch, car, timeStep):
        if self.autoAdderSwitch != True:
            self.autoAdderByTime = switch
            self.autoAdder = car
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
    def pCounter(self, carsNum, car):
        A = (carsNum/car.view)**self.alpha
        B = (car.v/self.vmax)**self.beta
        return A*B

    #计算车辆当前速度
    def getV(self, car, distance, p, slowVic):
        v = car.v
        offTouch = car.length/2 + car.vDistance
        voffset = car.acc
        negvoffset = car.negacc
        if car.v <= distance:
            if slowVic < p:
                if v - negvoffset > 0:
                    v -= negvoffset

                else:
                    v = 0
            else:
                if v + voffset < self.vmax:
                    v += voffset
                else:
                    v = self.vmax
        else:
            if v > 0 and distance - offTouch > 0:
                v = distance - negvoffset
            else:
                v = 0
        return v

#不作为类,用作为结构体,记录车的各种参数
class Car(object):
    def __init__(self):
        self.name = 'default'               #车类名称,用于统计
        self.length = 4.0                   #车身长度
        self.vDistance = 1                  #最小车距
        self.acc = 2.7                      #加速度/s
        self.negacc = 1.2                   #减速度/s
        self.view = 120                     #司机视野距离
        self.v = 0.0                        #当前速度
        self.locate = 0.0                   #当前位置  
        self.height = 0.0                   #汽车高度,暂时没用

#在指定长度上初始化指定数量的车辆,可以指定分布,默认线性均匀分布
#TODO:检查是否能初始化成功(根据路长、车长、车距)
def initCarsDistributed(length, carTemplate, initV, carsNum, lanes = 1, dis = 'linear'):
    if dis == 'linear':
        locate = np.linspace(0.0, length, num=carsNum)
    elif dis == 'c-uniform':
        locate = np.array(sorted(np.random.random(carsNum)*length))
    else:
        print 'No such distribution'
        return
    
    output = []
    for i in xrange(lanes):
        carBox = [copy.deepcopy(carTemplate) for i in xrange(carsNum) ]
        for index, car in enumerate(carBox):
            car.locate = locate[index]
            car.v = initV[index]
        output.append(np.array(carBox))

    return output
    
    #TODO:poisson分布需要另起一个函数啊....还得跑去啃下概率论的书QAQ
    #elif dis == 'poisson':
    #    pass
