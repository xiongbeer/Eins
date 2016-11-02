#!/usr/bin/env python
# coding=utf-8

#优化工作: 0%
#GUI: 0%
#TODO:x.append() + np.array() 的效率远高于 np.append!!!!!
#TODO:carBox = [np.array([])*N] -----> [[]*N]

import numpy as np
import copy

KKW_BASIC = {'vfree':30.0, 'd':7.5, 'p0':0.425}
KKW_1 = {'k':2.55, 'vp':14.0, 'pa1':0.2, 'pa2':0.052, 'p':0.04}
KKW_2 = {'p':0.04, 'pa':0.052, 'beta':0.05}
KKW_3 = {'p':0.04, 'beta':0.05}
KKW_4 = {'d1':2.5, 'k':2.55, 'p':0.04, 'pa':0.052}
FLOAT_PREC = 2

#不作为类,用作为结构体,记录车的各种参数
class Car:
    def __init__(self):
        self.name = 'default'               #车类名称,用于统计
        self.length = 1.0                   #车身长度
        self.vDistance = 0.0                #最小车距
        self.slowacc = 0.5                  #慢加速度/s
        self.acc = 1.0                      #加速度/s
        self.negacc = 1.0                   #减速度/s
        self.view = 0                       #司机视野距离
        self.v = 0.0                        #当前速度
        self.locate = 0.0                   #当前所在位置
        self.lane = 0                       #当前所在车道
        self.height = 0.0                   #汽车高度,暂时没用
        self.bn = False                     #刹车灯
        self.tst = 0                        #敏感时间
        self.stoped = False                 #上一个时刻受到了阻挡后刹车的标记

class Road(object):
    'Road && Cars'

    def __init__(self, carBox_, vmax_, length_, target_ = 0.0, lanes_ = 1,
                 enterCars_ = 0, enterFlag_ = False, connectRoad_ = None):
        self.carBox = carBox_                   #道路上所有车辆及其具体状态和参数
        self.enterCars = enterCars_             #已进入此路的车辆数
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
        self.alpha = 0.6                        #减速概率的alpha因子,不能随意修改,除非你知道自己在干什么
        self.beta = 0.2                         #减速概率的beta因子,同上
        self.autoAdderSwitch = False            #是否自动添加车辆
        self.autoAdderByTime = False            #是否按时间自动添加车辆,与前一个Flag冲突
        self.autoAdder = None                   #自动添加车辆的初始速度
        self.connectRoad = connectRoad_         #连接的公路(入口),默认值为空
        self.autoAddTime = 0                    #用户定义的自动添加车辆的时间间隔
        self.timeCounter = 0                    #系统内部用于自动添加车辆的时间计数器
        self.wholeTime = 0                      #总的运行时间
        self.stableP = 0.4                      #固定减速因子,一旦设定,那么alpha和beta就会失效
        self.waitLine = []                      #等待添加的车辆列队

    def __str__(self):
        des = '\n车道数:'+str(self.lanes)+'\n道路长度:'+str(self.length+self.target)+'\n运行时间(/s):'+str(self.wholeTime)+'\n是否为入口:'+str(self.enterFlag)
        carsCounter = []
        for index, lane in enumerate(self.carBox):
            carsCounter.append(len(lane))
            des += '\n'+'车量-车道'+str(index)+':'+str(len(lane))
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

    def ViewCars(self, car, viewBox, offset = 0.0):
        tempLocate = np.array([])
        for locate in viewBox:
            tempLocate = np.append(tempLocate, locate.v)
        temp = car.locate + car.view - tempLocate - offset
        temp = temp[temp >= 0]
        return temp.size

    #考虑视野距离计算实时随机减速概率
    def pCounter(self, carsNum, car):
        A = (float(carsNum)/car.view)**self.alpha
        B = (car.v/self.vmax)**self.beta
        return A*B

    def setAlphaBeta(self, alpha_, beta_):
        self.alpha = alpha_
        self.beta = beta_
    def setStabelP(self, p):
        self.stableP = p
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
    def getExecTime(self):
        return self.wholeTime

    #=====================模型=========================

    #慢启动规则
    def TT(self, car, nextCar, pt):
        if car.v == 0:
            if nextCar != None:
                if (car.length + nextCar.length)/2 +car.vDistance < nextCar.locate - car.locate <= (car.length + nextCar.length) + car.vDistance*2:
                    return 1.0 - pt
            else:
                return None
        else:
            return None

    def BJH(self, flag, ps):
        if flag:
            return 1.0 - ps
        else:
            return 0

    def VDR(self, flag, p0):
        if flag == False:
            return self.stableP
        else:
            return p0

    #减速规则
    def VE(self, car ,nextCar, next2Car):
        dn = (car.length + nextCar.length)/2 + car.vDistance
        dnc = (nextCar.length + next2Car.length)/2 + nextCar.vDistance
        vc = min(self.vmax - car.acc, nextCar.v, max(0,dnc - nextCar.acc))
        car.v = min(car.v + car.acc, dn + vc)

    #Kerner,Klenov,Wolf's Models
    def KKW(self, car, nextCar, modelKind, modelPara):
        #参数确定
        #paras needs:vfree,d,p0
        dn = (car.length + nextCar.length)/2 + car.vDistance
        gn = nextCar.locate - car.locate - dn

        #request paras:k,p0,p,pa1,pa2,vp
        if modelKind == 1:
            D = modelPara['d'] + modelPara['k']*car.v*tao
            if car.v > 0:
                pb = modelPara['p']
            else:
                pb = modelPara['p0']

            if car.v < vp:
                pa = modelPara['pa1']
            else:
                pa = modelPara['pa2']

        #request paras:beta,p0
        elif modelKind == 2:
            D = modelPara['d'] + car.v*tao + modelPara['beta']*np.power(car.v, 2)/(car.acc*2)
            if car.v > 0:
                pb = modelPara['p']
            else:
                pb = modelPara['p0']

        #request paras:pa=0,beta,p0,p
        elif modelKind == 3:
            D = modelPara['d'] + car.v*tao + modelPara['beta']*np.power(car.v, 2)/(car.acc<<1)
            if 0 < car.v < modelPara['vfree']:
                pb = modelPara['p']
            elif car.v == 0:
                pb = modelPara['p0']
            elif car.v == modelPara['vfree']:
                pb = 0

        #request paras:d1<d,k,p0,p,pa
        elif modelKind == 4:
            D = modelPara['d1'] + modelPara['k']*car.v*tao
            if car.v > 0:
                pb = modelPara['p']
            else:
                pb = modelPara['p0']
        else:
            print 'Unkonw modelKind'

        #TODO:tao
        vsafe = gn/tao

        #随机过程
        if gn > D - dn:
            vdes = car.v + car.acc*tao
        else:
            vdes = car.v + car.acc*tao*np.sign(nextCar.v - car.v)

        vc = max(0, min(vfree, vsafe, vdes))

        #确定过程
        rand = np.random.random()
        if rand < pb:
            era = -1
        elif pb <= rand < pb + pa:
            era = 1
        else:
            era = 0
        car.v = max(0,min(vc + car.acc*tao*era, vc + car.acc*tao, vfree, vsafe))

        car.locate += car.v

    #==================================================
    #减少需要进入其他道路车辆的计数,并且返回那辆车的信息
    def reduceEndCars(self):
        car = self.endCars[0]
        self.endCars = np.delete(self.endCars, 0)
        return car

    #抽象函数
    def reflushStatus(self):
        pass

    def reflushWaitLine(self, opLane):

        if len(self.waitLine) != 0:
            opCar = self.waitLine[0]
            #车辆优先进入相同车道标号的车道
            if opCar.lane == opLane:
                if len(self.carBox[opLane]) != 0:
                    if  self.carBox[opLane][0].locate - opCar.locate >= (opCar.length + self.carBox[opLane][0].length)/2 + opCar.vDistance:
                        self.carBox[opLane].insert(0, opCar)
                        del self.waitLine[0]
                    else:
                        pass
                else:
                    self.carBox[opLane].append(opCar)
                    del self.waitLine[0]
            else:
                pass
        else:
            pass

    def addCar(self, car):
        car = copy.deepcopy(car)    #深复制一个对象(新建一辆车)
        self.enterCars += 1
        self.waitLine.append(car)

    #清空离开道路车辆数的计数
    def reLeave(self):
        self.leaveCars = [0]*self.lanes

    #自动添加车辆(每离开一辆就添加一辆)
    def addCarAutomaticByBound(self, switch, car):
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
            if timeStep <= 0:
                self.autoAddTime = timeStep
            else:
                print 'timeStep must bigger than ZERO'
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

    def getNextEnterLane(self):
        number = self.laneFlag
        if number + 1 < self.lanes:
            number += 1
        else:
            number = 0
        return number

class NSRoad(Road):
    def __init__(self, carBox_, vmax_, length_, target_ = 0.0, lanes_ = 1,
                 enterCars_ = 0, enterFlag_ = False, connectRoad_ = None):
        super(NSRoad, self).__init__(carBox_, vmax_, length_, target_ , lanes_,
                     enterCars_, enterFlag_ , connectRoad_)
        self.TTFlag = False
        self.TTPt = 0

        self.BJHFlag = False
        self.BJHPs = 0
        self.BJHflag = False

        self.VDRFlag = False
        self.VDRP0 = 0

        self.VEFlag = False

    def setTT(self, switch, TTPt_ = 0.75):
        self.TTFlag = switch
        if switch == True:
            self.TTPt = TTPt_

    def setBJH(self, switch, BJHPs_ = 0.75):
        self.BJHFlag = switch
        if switch == True:
            self.BJHPS = BJHPs_

    def setVDR(self, switch, VDRP0_ = 0.75):
        self.VDRFlag = switch
        if switch == True:
            self.VDRP0 = VDRP0_

    def setVE(self, switch):
        self.VEFlag = switch

    #最基础的NS模型
    def NS(self, car, nextCar):
        #step1:加速
        if self.TTFlag:
            tempP = self.TT(car, nextCar, self.TTPt)
            if tempP == None or np.random.random() < tempP:
                car.v = min(car.v + car.acc, self.vmax)

        else:
            car.v = min(car.v + car.acc, self.vmax)

        if self.BJHFlag:
                tempP = self.BJH(car.stoped, self.BJHPs)
                if np.random.random() < tempP:
                    car.v = 0
        if self.BJHFlag or self.VDRFlag:
            car.stoped = False

        #step2:减速
        if nextCar != None:
            dn = (car.length+nextCar.length)/2 + car.vDistance
            distance = nextCar.locate - car.locate
        else:
            dn = 0.0
            distance = car.v*2
        if car.v + dn >= distance:
            d = max(0, distance - dn)
            car.v = min(car.v, d)
            if (self.VDRFlag or self.BJHFlag) and car.v == 0:
                car.stoped = True

        #step3:随机慢化
        if self.VDRFlag:
            tempP = self.VDR(car.stoped, self.VDRP0)
            if np.random.random() < tempP:
                car.v = max(car.v - car.negacc, 0)
        elif np.random.random() < self.stableP:
            car.v = max(car.v - car.negacc, 0)

        #step4:运动
        car.locate += car.v

    def reflushStatus(self):
        self.timer()
        #每个车道分别计算,也就是车不会中途改变车道
        for lane in xrange(0,self.lanes):
            if len(self.carBox[lane]) == 0:
                continue
            if len(self.carBox[lane]) >= 2:
                for i in xrange(0, len(self.carBox[lane]) - 1):
                    opCar = self.carBox[lane][i]
                    opCar.lane = lane
                    nextCar = self.carBox[lane][i+1]
                    self.NS(opCar, nextCar)
            #最前的车单独计算
            opCar = self.carBox[lane][-1]
            opCar.lane = lane
            nextCar = None
            if self.connectRoad != None:
                opLane = self.connectRoad.getNextEnterLane()
                info = self.connectRoad.getCarsInfo()
                if len(info[opLane]) > 0:
                    nextCar = info[opLane][0]
            self.NS(opCar, nextCar)
            #到达尽头后移除车辆,增加endCarsV的值，代表有车需要进入其他道路
            if opCar.locate >= self.length + self.target:
                opCar.locate = 0.0
                self.endCars = np.append(self.endCars, opCar)
                del self.carBox[lane][-1]
                self.leaveCars[lane] += 1
                #如果出口连接了其他的道路,则自动将离开的车加入其入口
                if self.connectRoad != None:
                    self.connectRoad.addCar(opCar)
                #如果需要自动添加车辆,每离开一辆车就自动在起始初添加一辆车(一般用于入口)
                if self.autoAdderSwitch == True:
                    self.addCar(self.autoAdder)
            self.reflushWaitLine(lane)
        #如果有需要,按时间添加车辆的LOOP
        if self.autoAdderByTime == True:
            if self.autoAddTime == self.timer(get = True):
                self.timer(reset = True)
                self.addCar(self.autoAdder)

class CDRoad(Road):
    def __init__(self, carBox_, vmax_, length_, target_ = 0.0, lanes_ = 1,
                 enterFlag_ = False, connectRoad_ = None,
                 h_=6, gap_=7, pb_=0.94, p0_=0.5, pd_=0.1):
        super(CDRoad, self).__init__(carBox_, vmax_, length_, target_ = 0.0, lanes_ = 1)
        self.h = h_
        self.gap = gap_
        self.pb = pb_
        self.p0 = p0_
        self.pd = pd_
    #舒适驾驶模型
    def CD(self, car, nextCar, next2Car):
        #if next2Car == None:
        if nextCar == None:
            nextCar = Car()
            nextCar.v = self.vmax
            nextCar.locate = self.length + ((car.length + nextCar.length)/2 + car.vDistance) + self.vmax
        dn = nextCar.locate - car.locate - ((car.length + nextCar.length)/2 + car.vDistance)


        #if dn < 0:
        #    dn = 0
        #dnc = next2Car.locate - nextCar.locate - (nextCar.length + next2Car.length)/2 + nextCar.vDistance
        dnc = 1000000.0
        if car.v != 0:
            th = dn/car.v
        else:
            th = 10000
        ts = min(car.v, self.h)
        vanti = min(dnc, nextCar.v)
        deff = max(dn + max(vanti - self.gap, 0), 0)
        #step1:确定随机慢化概率p
        if nextCar.bn == 1 and th < ts:
            p = self.pb
        elif car.v == 0:
            p = self.p0
        else:
            p = self.pd
        nextbn = 0
        #step2:加速
        if (nextCar.bn == 0 and car.bn == 0) or (th >= ts):
            nextv = min(car.v + car.acc, self.vmax)
        else:
            nextv = car.v
        #step3:减速
        nextv = min(deff, nextv)
        if nextv < car.v:
            nextbn = 1
        #step4:慢化
        if np.random.random() <= p:
            nextv = max(nextv - car.negacc, 0)
            if p == self.pb:
                nextbn = 1
        #step5:更新速度
        return nextv
    def reflushStatus(self):
        self.timer()
        #每个车道分别计算,也就是车不会中途改变车道
        for lane in xrange(0,self.lanes):
            tempVSaver = []
            tempLocateSaver = []
            if len(self.carBox[lane]) == 0:
                continue
            if len(self.carBox[lane]) >= 2:
                for i in xrange(0, len(self.carBox[lane]) - 1):
                    opCar = self.carBox[lane][i]
                    nextCar = self.carBox[lane][i+1]
                    try:
                        next2Car = self.carBox[lane][i+2]
                    except:
                        next2Car = None
                    v = self.CD(opCar, nextCar, next2Car)
                    tempVSaver.append(v)
                    tempLocateSaver.append(opCar.locate + v)
            #最前的车单独计算
            opCar = self.carBox[lane][-1]
            nextCar = None
            next2Car = None
            if self.connectRoad != None:
                opLane = self.connectRoad.getNextEnterLane()
                info = self.connectRoad.getCarsInfo()
                if len(info[opLane]) > 0:
                    nextCar = info[opLane][0]
                    if len(info[opLane]) > 1:
                        next2Car = info[opLane][1]
            v = self.CD(opCar, nextCar, next2Car)
            tempVSaver.append(v)
            tempLocateSaver.append(opCar.locate + v)
            #到达尽头后移除车辆,增加endCarsV的值，代表有车需要进入其他道路
            #在CD模型中,可能会有多辆车在时间间隔内到达道路终点
            counter = 0         #记录有多少辆车需要离开道路
            for i in xrange(len(tempVSaver)):
                opCar = self.carBox[lane][i]
                opCar.v = tempVSaver[i]
                opCar.locate = tempLocateSaver[i]
                if opCar.locate >= self.length:
                    counter += 1

            for i in xrange(counter):
                opCar = self.carBox[lane][-1]
                opCar.locate -= self.length
                self.endCars = np.append(self.endCars, opCar)
                self.carBox[lane] = np.delete(self.carBox[lane], -1)
                self.leaveCars[lane] += 1
                #如果出口连接了其他的道路,则自动将离开的车加入其入口
                if self.connectRoad != None:
                    self.connectRoad.addCar(opCar)
                #如果需要自动添加车辆,每离开一辆车就自动在起始初添加一辆车(一般用于入口)
                if self.autoAdderSwitch == True:
                    self.addCar(self.autoAdder)

        #如果有需要,按时间添加车辆的LOOP
        if self.autoAdderByTime == True:
            if self.autoAddTime == self.timer(get = True):
                self.timer(reset = True)
                self.addCar(self.autoAdder)
class MCDRoad(Road):
    def __init__(self):
        super(Road, self).__init__(self, carBox_, vmax_, length_, target_ = 0.0, lanes_ = 1,
                     enterCars_ = 0, enterFlag_ = False, connectRoad_ = None)


    #改进的CD模型
    def MCD(self, car, h, gap, nextCar, next2Car, tc ):
        dn = (car.length + nextCar.length)/2 + car.vDistance
        dnc = (nextCar.length + next2Car.length)/2 + nextCar.vDistance
        th = dn/car.v
        ts = min(car.v, h)
        vanti = min(dnc, nextCar.v)
        deff = dn + max(vanti - gap, 0)

        #step1:确定随机慢化概率
        if nextCar.bn == 1 and th < ts:
            p = pb
        elif car.v == 0 and car.tst >= tc:
            p = p0
        else:
            p = pd

        #step2:加速
        if (nextCar.bn == 0 or th >= ts) and car.v > 0:
            nextv = min(car.v + car.acc, self.vmax)
        elif car.v == 0:
            nextv = min(car.v + car.slowacc, self.vmax)
        else:
            nextv = car.v

        #step3:减速
        nextv = min(deff, nextv)

        #step4:慢化
        if randomMake <= p:
            nextv = max(nextv - car.negacc, 0)

        #step5:确定刹车灯状态bnc
        if nextv < car.v:
            nextbn = 1
        elif nextv > car.v:
            nextbn = 0
        else:
            nextbn = car.bn

        #step6:确定tst
        if nextv > 0:
            car.tst = 0
        elif nextv == 0:
            car.tst += 1

        #step7:位置更新
        car.v = nextv
        car.locate += car.v
    def reflushStatus(self):
        self.timer()
        #每个车道分别计算,也就是车不会中途改变车道
        for lane in xrange(0,self.lanes):
            if len(self.carBox[lane]) == 0:
                continue
            slowVic = np.random.random(len(self.carBox[lane]))
            if len(self.carBox[lane]) >= 2:
                for i in xrange(0, len(self.carBox[lane]) - 1):
                    opCar = self.carBox[lane][i]
                    nextCar = self.carBox[lane][i+1]
                    self.NS(opCar, nextCar)
            #最前的车单独计算
            opCar = self.carBox[lane][-1]
            nextCar = None
            if self.connectRoad != None:
                opLane = self.connectRoad.getNextEnterLane()
                info = self.connectRoad.getCarsInfo()
                if len(info[opLane]) > 0:
                    nextCar = info[opLane][0]
            self.NS(opCar, nextCar)
            #到达尽头后移除车辆,增加endCarsV的值，代表有车需要进入其他道路
            if opCar.locate > self.length + self.target:
                opCar.locate = 0.0
                self.endCars = np.append(self.endCars, opCar)
                self.carBox[lane] = np.delete(self.carBox[lane], -1)
                self.leaveCars[lane] += 1
                #如果出口连接了其他的道路,则自动将离开的车加入其入口
                if self.connectRoad != None:
                    self.connectRoad.addCar(opCar)
                #如果需要自动添加车辆,每离开一辆车就自动在起始初添加一辆车(一般用于入口)
                if self.autoAdderSwitch == True:
                    self.addCar(self.autoAdder)

        #如果有需要,按时间添加车辆的LOOP
        if self.autoAdderByTime == True:
            if self.autoAddTime == self.timer(get = True):
                self.timer(reset = True)
                self.addCar(self.autoAdder)

class ProcessWriter(object):
    def __init__(self, road_, label_, plantime_):
        self.road = road_
        self.label = label_
        self.savePath = r'./'+'ProcessInfo_'+label_+r'.csv'
        self.setFlag = False
        self.outputFlow = None
        self.plantime = plantime_

    def reSetPath(self, path):
        if self.setFlag != True:
            self.savePath = path
        else:
            print 'alreadly init'

    def setInit(self):
        if self.setFlag != True:
            self.outputFlow = open(self.savePath,'w+')
            self.outputFlow.write('Time Locate V\n')
            self.outputFlow.write(str(self.plantime) + ' ' + str(self.road.getRoadLanes()) + ' ' +
                    str(self.road.getRoadLength()) + '\n')
            self.setFlag = True

    def writeInfo(self):
        if self.setFlag == True:
            flag = False
            carBox = self.road.getCarsInfo()
            outputLocate = ''
            outputV = ''
            for lane in carBox:
                if flag == False:
                    flag = True
                else:
                    outputLocate += ':'
                    outputV += ':'
                for i in xrange(len(lane)):
                    outputLocate += (str(round(lane[i].locate, FLOAT_PREC)))
                    outputV += (str(round(lane[i].v, FLOAT_PREC)))
                    if i != len(lane)-1:
                        outputLocate += ','
                        outputV += ','
            #这里的-1只是一个占位符号,并没有实际用处,作用是防止在只有一辆车的时候pandas读取报错
            if outputLocate != '':
                self.outputFlow.write(str(self.road.getExecTime())+' '+'-1,'+outputLocate+' '+'-1,'+outputV+'\n')
        else:
            raise 'write failed'
    def cleanAll(self):
        self.outputFlow.close()

def initEmptyRoad(lanes):
    output = []
    for i in xrange(lanes):
        output.append(np.array([],dtype='object'))
    return output

#在指定长度上初始化指定数量的车辆,可以指定分布,默认线性均匀分布
#TODO:检查是否能初始化成功(根据路长、车长、车距)
def initCarsDistributed(length, carTemplate, initV, carsNum, lanes = 1, dis = 'linear'):
    if length <= 0 or carsNum <= 0:
        raise 'InitFailed'

    if dis == 'linear':
        locate = np.linspace(0.0, length, num = carsNum)
        if carsNum != 1:
            for i in xrange(0, locate.size - 1):
                if locate[i+1] - locate[i] < carTemplate.length + carTemplate.vDistance:
                    raise 'InitFailed'

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
        output.append(carBox)

    return output

    #TODO:poisson分布需要另起一个函数啊....还得跑去啃下概率论的书QAQ
    #elif dis == 'poisson':
    #    pass
