#!/usr/bin/env python
# coding=utf-8

import numpy as np
import copy
import math
import tips

KKWModel = {

}


#不作为类,用作为结构体,记录车的各种参数
class Car(object):
    def __init__(self):
        self.name = 'default'               #车类名称,用于统计
        self.length = 1.0                   #车身长度
        self.safedistance = 0.0             #最小车距
        self.slowacc = 0.5                  #慢加速度/s
        self.acc = 1.0                      #加速度/s
        self.negacc = 1.0                   #减速度/s
        self.view = 0                       #司机视野距离
        self.speed = 0.0                    #当前速度
        self.locate = 0.0                   #当前所在位置
        self.lane = 0                       #当前所在车道
        self.height = 0.0                   #汽车高度,暂时没用
        self.bn = False                     #刹车灯
        self.tst = 0                        #敏感时间
        self.stoped = False                 #上一个时刻受到了阻挡后刹车的标记
        self.changeflag = False

class Road(object):
    'Road && Cars'

    def __init__(self, carbox, vmax, length, lanes=1,
                 entercars=0, enterflag=False, connectroad=None, exitflag=False, roadname='default'):
        self.carbox = carbox                    #道路上所有车辆及其具体状态和参数
        self.entercars = entercars              #已进入此路的车辆数
        self.leavecars = np.zeros(lanes)              #离开此路的车辆数
        self.vmax = float(vmax)                 #道路最大车速
        self.length = float(length)             #道路长度
        self.lanes = int(lanes)                 #车道数,默认为单车道
        self.endcars = np.array([])             #list的长度表示有多少车辆需要进入其他道路,键值为其速度
        self.enterflag = enterflag              #标记此道是否是入口
        self.exitflag = exitflag                #标记此道是否是出口

        self.changeswitch = False               #是否打开换道功能
        self.alpha = 0.6                        #减速概率的alpha因子,不能随意修改,除非你知道自己在干什么
        self.beta = 0.2                         #减速概率的beta因子,同上
        self.autoAdderSwitch = False            #是否自动添加车辆
        self.autoAdderByTime = False            #是否按时间自动添加车辆,与前一个Flag冲突
        self.autoAdderBox = None                #自动添加车辆的初始速度
        self.connectroad = connectroad          #连接的公路(入口),默认值为空
        self.autoAddTime = 0                    #用户定义的自动添加车辆的时间间隔
        self.timeCounter = 0                    #系统内部用于自动添加车辆的时间计数器
        self.wholeTime = 0                      #总的运行时间
        self.stableP = 0.4                      #固定减速因子,一旦设定,那么alpha和beta就会失效
        self.waitLine = []                      #等待添加的车辆列队
        self.pers = None
        self.roadname = roadname
    def __iter__(self):
        self.iterindex = -1
        return self

    def next(self):
        self.iterindex += 1
        if self.iterindex >= self.lanes:
            raise StopIteration
        return self.carbox[self.iterindex]

    def shape(self):
        output = []
        for lane in self.carbox:
            output.append(len(lane))
        return output

    def __len__(self):
        output = 0
        for lane in self.carbox:
            output += len(lane)
        return output

    #标记线内的为public func
    #-----------------------------------------------------
    def get_cars_locate(self):
        output = []
        for lane in self.carbox:
            output.append(np.array([car.locate for car in lane]))
        return output

    def get_cars_v(self):
        output = []
        for lane in self.carbox:
            output.append(np.array([car.speed for car in lane]))
        return output

    def get_mean_speed(self):
        carsvbox = self.get_cars_v()
        output = np.array([])
        counter = 0
        adder = 0.0
        for lane in carsvbox:
            if lane.size != 0:
                value = lane.mean()
                counter += 1
                output = np.append(output, value)
                adder += value
            else:
                output = np.append(output, -1)
        if counter != 0:
            whole = adder/counter
        else:
            whole = None
        return output, whole

    def __view_cars(self, car, viewBox, offset=0.0):
        tempLocate = np.array([])
        for locate in viewBox:
            tempLocate = np.append(tempLocate, locate.speed)
        temp = car.locate + car.view - tempLocate - offset
        temp = temp[temp >= 0]
        return temp.size

    #考虑视野距离计算实时随机减速概率
    def pcounter(self, carsNum, car):
        A = (float(carsNum)/car.view)**self.alpha
        B = (car.speed/self.vmax)**self.beta
        return A*B

    def set_alpha_beta(self, alpha, beta):
        self.alpha = alpha
        self.beta = beta

    def set_stabel_p(self, p):
        self.stableP = p

    def get_cars(self):
        return self.carbox

    def get_road_lanes(self):
        return self.lanes

    def get_road_length(self):
        return self.length

    def get_road_vmax(self):
        return self.vmax

    def get_leave_cars(self):
        return self.leavecars

    def get_exec_time(self):
        return self.wholeTime

    def get_cars_num(self):
        output = np.zeros(self.lanes)
        for i in xrange(self.lanes):
            output[i] = len(self.carbox[i])
        return output

    #=====================模型=========================

    #慢启动规则
    def TT(self, car, nextCar, pt):
        if car.speed == 0:
            if nextCar != None:
                if (car.length + nextCar.length)/2 +car.safedistance < nextCar.locate - car.locate \
                     <= (car.length + nextCar.length) + car.safedistance*2:
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
    def VE(self, car, nextCar, next2Car):
        dn = (car.length + nextCar.length)/2 + car.safedistance
        dnc = (nextCar.length + next2Car.length)/2 + nextCar.safedistance
        vc = min(self.vmax - car.acc, nextCar.speed, max(0, dnc - nextCar.acc))
        car.speed = min(car.speed + car.acc, dn + vc)


class ExecRoad(Road):
    def __init__(self, carbox, vmax, length, lanes=1,
                 entercars=0, enterflag=False, connectroad=None, exitflag=False, roadname='default'):
        super(ExecRoad, self).__init__(carbox, vmax, length, lanes, \
                entercars, enterflag, connectroad, exitflag, roadname)

        self.set_MCD_para()
        self.execRule = self.NS


        self.TTFlag = False
        self.TTPt = 0

        self.BJHFlag = False
        self.BJHPs = 0
        self.BJHflag = False

        self.VDRFlag = False
        self.VDRP0 = 0

        self.VEFlag = False
        self.insertpostion = 0.0
        self.nextlanemethod = 'simple'

        self.headcountflag = True
        self.headfont = [0]*self.lanes
        self.head = []
        for i in xrange(self.lanes):
            self.head.append([])

    def __str__(self):
        if self.connectroad != None:
            crid = str(hex(id(self.connectroad)))
        else:
            crid = str(None)
        des =   '+===================+\n' + \
                ' - 运行规则及道路HashValue：' + str(self.execRule)  + \
                '\n - 车道数:'+str(self.lanes) + \
                ' - 道路长度(m):'+str(self.length) + \
                ' - 运行时间(s):'+str(self.wholeTime) + \
                ' - 是否为入口:'+str(self.enterflag) + \
                ' - 是否为出口:'+str(self.exitflag)

        carsCounter = []
        des += '\n --------------------'
        meanspeed, whole = self.get_mean_speed()
        if whole != None:
            whole = round(whole, 3)
        for index, lane in enumerate(self.carbox):
            if meanspeed[index] != -1:
                v = round(meanspeed[index], 3)
            else:
                v = None
            carsCounter.append(len(lane))
            des +=  '\n'+' - 车道_'+str(index) + \
                    ' - 车辆数目' +':'+str(len(lane)) + \
                    ' - 平均车速：' + str(v) + \
                    ' - 已通过车辆数：' + str(self.leavecars[index])

        des +=  '\n'+' -  整体  - 车辆数目:'+str(sum(carsCounter)) + \
                ' - 平均车速：' + str(whole) + \
                ' - 已通过车辆数：' + str(sum(self.leavecars)) + \
                '\n --------------------' + \
                '\n - 连接道路：' + crid + \
                ' - 时间边界条件：' + str(self.autoAdderByTime) + \
                ' - 循环边界条件：' + str(self.autoAdderSwitch) + \
                '\n+===================+\n'
        return des

    def set_exec_rule(self, rule):
        if rule == 'NS':
            self.execRule = self.NS
        elif rule == 'CD':
            self.execRule = self.CD
        elif rule == 'MCD':
            self.execRule = self.MCD
        elif rule == 'KKW':
            self.execRule = self.KKW
        else:
            raise KeyError('No that exec rule')

    def get_head_t(self):
        return self.head

    def set_MCD_para(self, h=6, gap=7, pb=0.94, p0=0.5, \
                    pd=0.1, tc=10):
        self.h = h
        self.gap = gap
        self.pb = pb
        self.p0 = p0
        self.pd = pd
        self.tc = tc

    def set_TT(self, switch, TTPt=0.75):
        self.TTFlag = switch
        if switch == True:
            self.TTPt = TTPt

    def set_BJH(self, switch, BJHPs=0.75):
        self.BJHFlag = switch
        if switch == True:
            self.BJHPS = BJHPs

    def set_VDR(self, switch, VDRP0=0.75):
        self.VDRFlag = switch
        if switch == True:
            self.VDRP0 = VDRP0

    def set_VE(self, switch):
        self.VEFlag = switch

    #最基础的NS模型
    def NS(self, car, nextCar, para):
        #step1:加速
        if self.TTFlag:
            tempP = self.TT(car, nextCar, self.TTPt)
            if tempP == None or np.random.random() < tempP:
                car.speed = min(car.speed + car.acc, self.vmax)

        else:
            car.speed = min(car.speed + car.acc, self.vmax)

        if self.BJHFlag:
            tempP = self.BJH(car.stoped, self.BJHPs)
            if np.random.random() < tempP:
                car.speed = 0
        if self.BJHFlag or self.VDRFlag:
            car.stoped = False

        #step2:减速
        if nextCar != None:
            dn = (car.length+nextCar.length)/2 + car.safedistance
            distance = nextCar.locate - car.locate
        else:
            dn = 0.0
            distance = car.speed*2

        if car.speed + dn >= distance:
            d = max(0, distance - dn)
            car.speed = min(car.speed, d)
            if (self.VDRFlag or self.BJHFlag) and car.speed == 0:
                car.stoped = True

        #step3:随机慢化
        if self.VDRFlag:
            tempP = self.VDR(car.stoped, self.VDRP0)
            if np.random.random() < tempP:
                car.speed = max(car.speed - car.negacc, 0)
        elif np.random.random() < self.stableP:
            car.speed = max(car.speed - car.negacc, 0)


        #step4:运动
        return car.speed

    #舒适驾驶模型
    def CD(self, car, nextCar, next2Car):
        ts = min(car.speed, self.h)
        if nextCar != None:
            nextCarbn = nextCar.bn
            dn = nextCar.locate - car.locate - (car.length + nextCar.length)/2 - car.safedistance
        else:
            nextCarbn = 0
            dn = ts*car.speed + 1
        if car.speed != 0:
            th = dn/car.speed
        else:
            th = ts + 1
        #step1:确定随机慢化概率p
        if nextCarbn == 1 and th < ts:
            p = self.pb
        elif car.speed == 0:
            p = self.p0
        else:
            p = self.pd
        nextbn = 0
        #step2:加速
        if (nextCarbn == 0 and car.bn == 0) or (th >= ts):
            nextv = min(car.speed + car.acc, self.vmax)
        else:
            nextv = car.speed
        #step3:减速
        if nextCar == None:
            deff = nextv + 1
        else:
            if next2Car == None:
                dnc = nextCar.speed + 1
            else:
                dnc = next2Car.locate - nextCar.locate - (nextCar.length + next2Car.length)/2\
                     - nextCar.safedistance
            vanti = min(dnc, nextCar.speed)
            deff = max(dn + max(vanti - self.gap, 0), 0)

        nextv = min(deff, nextv)
        if nextv < car.speed:
            nextbn = 1
        #step4:慢化
        if np.random.random() <= p:
            nextv = max(nextv - car.negacc, 0)
            if p == self.pb:
                nextbn = 1
        #step5:更新速度
        return nextv

    #改进的CD模型
    def MCD(self, car, nextCar, next2Car):
        ts = min(car.speed, self.h)
        if nextCar != None:
            nextCarbn = nextCar.bn
            dn = nextCar.locate - car.locate - (car.length + nextCar.length)/2 - car.safedistance
        else:
            nextCarbn = 0
            dn = ts*car.speed + 1
        if car.speed != 0:
            th = dn/car.speed
        else:
            th = ts + 1

        #step1:确定随机慢化概率
        if nextCarbn == 1 and th < ts:
            p = self.pb
        elif car.speed == 0 and car.tst >= self.tc:
            p = self.p0
        else:
            p = self.pd

        #step2:加速
        if (nextCarbn == 0 or th >= ts) and car.speed > 0:
            nextv = min(car.speed + car.acc, self.vmax)
        elif car.speed == 0:
            nextv = min(car.speed + car.slowacc, self.vmax)
        else:
            nextv = car.speed

        #step3:减速
        if nextCar == None:
            deff = nextv + 1
        else:
            if next2Car == None:
                dnc = nextCar.speed + 1
            else:
                dnc = next2Car.locate - nextCar.locate - (nextCar.length + next2Car.length)/2 \
                - nextCar.safedistance
            vanti = min(dnc, nextCar.speed)
            deff = max(dn + max(vanti - self.gap, 0), 0)

        nextv = min(deff, nextv)

        #step4:慢化
        if np.random.random() <= p:
            nextv = max(nextv - car.negacc, 0)

        #step5:确定刹车灯状态bnc
        if nextv < car.speed:
            nextbn = 1
        elif nextv > car.speed:
            nextbn = 0
        else:
            nextbn = car.bn

        #step6:确定tst
        if nextv > 0:
            car.tst = 0
        else:
            car.tst += 1

        #step7:位置更新
        return nextv

    def KKW(self, car, nextCar, para, model = KKWModel):
        #参数确定
        #paras needs:vfree,d,p0
        dn = (car.length + nextCar.length)/2 + car.safedistance
        gn = nextCar.locate - car.locate - dn

        #request paras:k,p0,p,pa1,pa2,vp
        if self.modelKind == 1:
            D = model['d'] + model['k']*car.speed*tao
            if car.speed > 0:
                pb = model['p']
            else:
                pb = model['p0']

            if car.speed < vp:
                pa = model['pa1']
            else:
                pa = model['pa2']

        #request paras:beta,p0
        elif self.modelKind == 2:
            D = model['d'] + car.speed*tao + model['beta']\
                *np.power(car.speed, 2)/(car.acc*2)
            if car.speed > 0:
                pb = model['p']
            else:
                pb = model['p0']

        #request paras:pa=0,beta,p0,p
        elif self.modelKind == 3:
            D = model['d'] + car.speed*tao + model['beta']\
                    *np.power(car.speed, 2)/(car.acc<<1)
            if 0 < car.speed < model['vfree']:
                pb = model['p']
            elif car.speed == 0:
                pb = model['p0']
            elif car.speed == model['vfree']:
                pb = 0

        #request paras:d1<d,k,p0,p,pa
        elif self.modelKind == 4:
            D = model['d1'] + model['k']*car.speed*tao
            if car.speed > 0:
                pb = model['p']
            else:
                pb = model['p0']
        else:
            print 'Unkonw modelKind'

        vsafe = gn/self.tao

        #随机过程
        if gn > D - dn:
            vdes = car.speed + car.acc*self.tao
        else:
            vdes = car.speed + car.acc*self.tao*np.sign(nextCar.speed - car.speed)

        vc = max(0, min(vfree, vsafe, vdes))

        #确定过程
        rand = np.random.random()
        if rand < pb:
            era = -1
        elif pb <= rand < pb + pa:
            era = 1
        else:
            era = 0
        car.speed = max(0, min(vc + car.acc*tao*era, vc + car.acc*tao, vfree, vsafe))

        return car.speed

    def reflush_status(self):
        self.__timer()
        # 换道
        if self.changeswitch is True:
            changebox = []
            for lane in self.carbox:
                it = iter(lane)
                while True:
                    try:
                        opcar = next(it)
                        try:
                            nextCar = next(it)
                        except StopIteration:
                            nextCar = None
                        if self.__change_lane(opcar, nextCar) is True:
                            changebox.append(opcar)
                    except StopIteration:
                        break

            for car in changebox:
                car.changeflag = False

        # 并行更新
        for lane in xrange(0, self.lanes):
            tempVSaver = []
            tempLocateSaver = []
            if len(self.carbox[lane]) == 0:
                continue
            if len(self.carbox[lane]) >= 2:
                for i in xrange(0, len(self.carbox[lane]) - 1):
                    opcar = self.carbox[lane][i]
                    opcar.lane = lane
                    nextCar = self.carbox[lane][i+1]
                    try:
                        next2Car = self.carbox[lane][i+2]
                    except:
                        next2Car = None
                    speed = self.execRule(opcar, nextCar, next2Car)
                    tempVSaver.append(speed)
                    tempLocateSaver.append(opcar.locate + speed)
            #最前的车单独计算
            opcar = self.carbox[lane][-1]
            opcar.lane = lane
            nextCar = None
            next2Car = None
            
            # 连接处的前方车辆判断
            if self.connectroad != None:
                oplane = self.__get_next_enter_lane(opcar.lane)
                info = self.connectroad.get_cars()[oplane]

                if len(info) == 0:
                    pass
                else:
                    insertindex = 0
                    for car in info:
                        if car.locate > self.insertpostion:
                            break
                        else:
                            insertindex += 1
                    num = len(info[insertindex:])
                    if num == 0:
                        pass
                    elif num == 1:
                        nextCar = copy.deepcopy(info[insertindex])
                        nextCar.locate += (self.length - self.insertpostion)
                    elif num > 1:
                        nextCar = copy.deepcopy(info[insertindex])
                        nextCar.locate += (self.length - self.insertpostion)

                        next2Car = copy.deepcopy(info[insertindex+1])
                        next2Car.locate += (self.length - self.insertpostion)


            speed = self.execRule(opcar, nextCar, next2Car)
            tempVSaver.append(speed)
            tempLocateSaver.append(opcar.locate + speed)

            endcars = []
            for i in xrange(len(tempVSaver)):
                opcar = self.carbox[lane][i]
                opcar.speed = tempVSaver[i]
                opcar.locate = tempLocateSaver[i]
                if opcar.locate >= self.length:
                    endcars.append(opcar)

            # 计算时间车头距的指标
            if self.headcountflag is True:
                foo = len(endcars)
                if foo > 1:
                    for i in xrange(foo-1):
                        self.head[lane].append(0)
                    self.headfont[lane] = self.wholeTime
                elif foo == 1:
                    self.head[lane].append(self.wholeTime - self.headfont[lane])
                    self.headfont[lane] = self.wholeTime

            for opcar in endcars:
                opcar.locate -= self.length
                self.leavecars[lane] += 1
                #如果出口连接了其他的道路,则自动将离开的车加入其入口
                if self.connectroad != None:
                    opcar.locate += self.insertpostion
                    if self.nextlanemethod == 'simple':
                        self.connectroad.add_car(opcar, opcar.lane)
                    elif self.nextlanemethod == 'left':
                        self.connectroad.add_car(opcar, 0)
                    elif self.nextlanemethod == 'right':
                        self.connectroad.add_car(opcar, self.connectroad.get_road_lanes()-1)

                #如果需要自动添加车辆,每离开一辆车就自动在起始初添加一辆车(一般用于入口)
                if self.autoAdderSwitch == True:
                    if self.pers == None:
                        if len(self.carbox[lane]) == 0 or \
                                self.carbox[lane][0].locate > self.autoAdder[0].length:
                            self.add_car(self.autoAdder[0], opcar.lane)
                    else:
                        dice = np.random.random()
                        upper = 0.0
                        lower = 0.0
                        for i in xrange(len(self.pers)):
                            upper += self.pers[i]
                            if lower <= dice < upper:
                                if len(self.carbox[lane]) == 0 or \
                                    self.carbox[lane][0].locate > self.autoAdder[i].length:
                                    self.add_car(self.autoAdder[i], opcar.lane)
                                break
                            lower += self.pers[i]
                self.carbox[lane].remove(opcar)

        self.__reflush_wait_line()

        #如果有需要,按时间添加车辆的LOOP
        if self.autoAdderByTime == True:
            if self.autoAddTime == self.__timer(get=True):
                self.__timer(reset=True)
                for i in xrange(self.nums):
                    #TODO:添加其他lane-method
                    oplane = int(np.random.random()*self.lanes)
                    if self.pers == None:
                        if len(self.carbox[oplane]) == 0 or \
                                self.carbox[oplane][0].locate > self.autoAdder[0].length:
                            self.add_car(self.autoAdder[0], oplane)
                    else:
                        dice = np.random.random()
                        upper = 0.0
                        lower = 0.0
                        for i in xrange(len(self.pers)):
                            upper += self.pers[i]
                            if lower <= dice < upper:
                                if len(self.carbox[oplane]) == 0 or \
                                    self.carbox[oplane][0].locate > self.autoAdder[i].length:
                                    self.add_car(self.autoAdder[i], oplane)
                                break
                            lower += self.pers[i]


    def __reflush_wait_line(self):
        oplane = 0
        while(len(self.waitLine) != 0):
            opcar = self.waitLine[0]
            newcar = copy.deepcopy(opcar)
            if newcar.lane == oplane:
                self.carbox[oplane].insert(0, newcar)
                self.waitLine.remove(opcar)
            elif newcar.lane > self.lanes:
                oplane = np.random.random()*self.lanes
                self.carbox[oplane].insert(0, newcar)
                self.waitLine.remove(opcar)
            else:
                pass

            if oplane < self.lanes:
                oplane += 1
            else:
                oplane = 0

    def __change_lane(self, opcar, nextCar, Pignore=None):
        dis = self.vmax + opcar.safedistance + opcar.length
        #判断是否需要换道
        if opcar.changeflag is True or opcar.lane - 1 < 0 or opcar.lane + 1 >= self.lanes \
            or nextCar == None or nextCar.locate - opcar.locate > dis:
            return False
        if Pignore != None:
            if np.random.random() > Pignore:
                return False
        carsLocate = self.get_cars_locate()
        insertIndex = 0
        # 左道优先
        oplane = opcar.lane - 1
        carsDistance = opcar.locate - carsLocate[oplane]
        carsInBound = carsDistance[abs(carsDistance) <= dis]
        negflag = False
        if carsInBound.size == 0:
            for index, offset in enumerate(carsDistance):
                if offset > 0:
                    insertIndex = index + 1
                else:
                    insertIndex = index
                    break

            opcar.changeflag = True
            self.carbox[oplane].insert(insertIndex, opcar)
            self.carbox[opcar.lane].remove(opcar)
            opcar.lane = oplane
            return True

        # 右道
        oplane = opcar.lane + 1
        carsDistance = opcar.locate - carsLocate[oplane]
        carsInBound = carsDistance[abs(carsDistance) <= dis]
        if carsInBound.size == 0:
            insertIndex = carsDistance.size
            for index, offset in enumerate(carsDistance):
                if offset > 0:
                    insertIndex = index + 1
                else:
                    insertIndex = index
                    break
            opcar.changeflag = True
            self.carbox[oplane].insert(insertIndex, opcar)
            self.carbox[opcar.lane].remove(opcar)
            return True

        return False

    def add_car(self, car, lane):
        car = copy.deepcopy(car)    #深复制一个对象(新建一辆车)
        car.lane = lane
        self.entercars += 1
        self.waitLine.append(car)

    #清空离开道路车辆数的计数
    def reLeave(self):
        self.leavecars = np.zeros(self.lanes)

    #自动添加车辆(每离开一辆就添加一辆)
    def cycle_boundary_condition(self, switch, carTemplateBox, pers=None):
        if self.autoAdderByTime != True:
            self.pers = pers
            self.autoAdderSwitch = switch
            self.autoAdder = carTemplateBox
        else:
            print 'Set add car automatic failed,there alreadly existed another mode'

    #按时间间隔添加车辆,与前一个冲突
    def time_boundary_condition(self, switch, carTemplateBox, pers=None, timeStep=1, nums=1, method = 'random'):
        if self.autoAdderSwitch != True:
            self.pers = pers
            self.autoAdderByTime = switch
            self.autoAdder = carTemplateBox
            self.nums = nums
            self.timeboundmethod = method
            if timeStep > 0:
                self.autoAddTime = timeStep
            else:
                print 'timeStep must bigger than ZERO'
        else:
            print 'Set add car automatic by time failed,there alreadly existed another mode'

    def set_connect_to(self, road, insertpostion=0):
        self.connectroad = road
        self.insertpostion = insertpostion


    #---------------------------------------------------
    def __timer(self, get=False, reset=False):
        if get == True:
            return self.timeCounter
        if reset == True:
            self.timeCounter = 0
        else:
            self.wholeTime += 1
            self.timeCounter += 1


    def __get_next_enter_lane(self, oplane):
        if self.nextlanemethod == 'simple':
            if oplane >= self.connectroad.lanes:
                return self.connectroad.lanes - 1
            else:
                return oplane
        elif self.nextlanemethod == 'right':
            return self.connectroad.lanes - 1
        elif self.nextlanemethod == 'left':
            return 0
        else:
            raise KeyError('No such method')

    def set_next_lane_method(self, method):
        self.nextlanemethod = method 

def init_empty_road(lanes):
    if lanes <= 0 :
        raise 'InitFailed: lanes must greater than ZERO!'
    output = []
    for i in xrange(lanes):
        output.append([])
    return output

#在指定长度上初始化指定数量的车辆,可以指定分布,默认线性均匀分布
def init_cars_distributed(length, carTemplateBox, carsNum=None, lanes=1, dis='normal', pers=None):
    
    output = []
    if length <= 0:
        raise ValueError('InitFailed: Road length must greater than ZERO!')
    if carsNum <= 0 and carsNum != None:
        raise ValueError(tips.get_red_warning('InitFailed: Cars num must greater than ZERO! '))

    #if type(carTemplateBox) != list or type(carTemplateBox[0]) != type(Car):
    #    raise 'InitFailed: Unkonw car template type'

    # 最密填充
    if dis == 'maxium':
        if len(carTemplateBox) == 1 and pers == None:
            for lane in xrange(lanes):
                adder = 0.0
                temp = []
                while adder <= length:
                    newCar = copy.deepcopy(carTemplateBox[0])
                    newCar.locate = adder
                    newCar.lane = lane
                    adder += (newCar.length + newCar.safedistance)
                    temp.append(newCar)
                output.append(temp)
            return output
        elif len(carTemplateBox) == len(pers):
            if sum(pers) != 1.0:
                raise ValueError('InitFailed:')
            for lane in xrange(lanes):
                adder = 0.0
                temp = []
                while adder <= length:
                    dice = np.random.random()
                    upper = 0.0
                    lower = 0.0
                    for i in xrange(len(pers)):
                        upper += pers[i]
                        if lower <= dice < upper:
                            newCar = copy.deepcopy(carTemplateBox[i])
                            break
                        lower += pers[i]
                    newCar.locate = adder
                    newCar.lane = lane
                    adder += (newCar.length + newCar.safedistance)
                    temp.append(newCar)
                output.append(temp)
            return output
        else:
            raise KeyError('InitFailed: ')
    # 均匀填充
    elif dis == 'normal':
        output = []
        for i in xrange(lanes):
            output.append([])
        if len(carTemplateBox) == 1 and pers == None:
            adder = 0.0
            oplane = 0
        
            while adder <= length:
                newCar = copy.deepcopy(carTemplateBox[0])
                newCar.locate = adder
                newCar.lane = oplane
                if oplane+1 < lanes:
                    oplane += 1
                else:
                    oplane = 0
                adder += (newCar.length + newCar.safedistance*2)
                output[oplane].append(newCar)
            return output
        elif len(carTemplateBox) == len(pers):
            if sum(pers) != 1.0:
                raise ValueError('InitFailed:')
            adder = 0.0
            oplane = 0
            while adder <= length:
                dice = np.random.random()
                upper = 0.0
                lower = 0.0
                for i in xrange(len(pers)):
                    upper += pers[i]
                    if lower <= dice < upper:
                        newCar = copy.deepcopy(carTemplateBox[i])
                        break
                    lower += pers[i]
                newCar.locate = adder
                newCar.lane = oplane
                if oplane+1 < lanes:
                    oplane += 1
                else:
                    oplane = 0
                adder += (newCar.length + newCar.safedistance*2)
                output[oplane].append(newCar)
            return output
        else:
            raise KeyError('InitFailed: ')
    else:
        raise KeyError('No such method')
