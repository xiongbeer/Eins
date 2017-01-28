#!/usr/bin/env python
# coding=utf-8
import numpy as np
import basicroad as br

class RoadStatus(object):
    def __init__(self, road_, timeStep_ = 'sec'):
        self.road = road_
        self.timeUnit = timeStep_
        self.timer = 0
        if timeStep_ == 'hour':
            self.timeStep = 1*60*60
        elif timeStep_ == 'min':
            self.timeStep = 1*60
        elif timeStep_ == 'sec':
            self.timeStep = 1
        elif timeStep_ == 'day':
            self.timeStep = 1*60*60*24
      
    def __str__(self):
        des = '\n总体车流量('+self.timeUnit+'):'+str(self.meanTrafficVolume().sum())
        return des

    #车流量=离开车数/单位时间
    def meanTrafficVolume(self):
        if self.timer == self.timeStep:
            output = np.array([])
            leaveCars = self.road.getLeaveCars()
            for num in leaveCars:
                output = np.append(output, num)
            self.road.reLeave()
            self.timer = 0
            return output
        else:
            self.timer += 1
            return -1
    def getMeanCarsDistance(self, info):
        output = np.array([])
        for lane in info:
            temp = np.array([])
            for i in xrange(lane.size-1):
                temp = np.append(temp, lane[i+1].locate - lane[i].locate)
            output = np.append(output, temp.mean()  )
        return output
    
    def getMeanCarsLength(self, info):
        output = np.array([])
        for lane in info:
            output = np.append(output, ( np.array([car.length for car in lane]).mean() ))
        return output
    
    def getMeanCarsV(self, info):
        output = np.array([])
        for lane in info:
            output = np.append(output, ( np.array([car.v for car in lane]).mean() ))
        return output
