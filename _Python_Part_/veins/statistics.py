#!/usr/bin/env python
# coding=utf-8
import numpy as np
import road as rd
import pandas as pd


PREC =  3   # 精度
def road_runner(roadbox, exectime):
    for i in xrange(exectime):
        for road in roadbox:
            road.reflush_status()

class RoadStatus(object):
    def __init__(self, road, method = 'normal', timestep = 'sec'):
        self.road = road
        self.dataset = pd.DataFrame()
        self.method = method
        self.timecounter = 0
        self.perwhole = 0
        self.perlanedata = []
        for i in xrange(road.get_road_lanes()):
            self.perlanedata.append([])
        if timestep == 'sec':
            self.timestep = 1
        elif timestep == 'min':
            self.timestep = 60
        elif timestep == 'hour':
            self.timestep = 60*60
        else:
            raise KeyError('No such method')

    def timer(self):
        if self.timecounter != self.timestep:
            self.timecounter += 1
        else:
            self.timecounter = 0
    
    def get_flux(self):
        data = self.road.get_leave_cars()
        laneresult = []
        if self.method == 'normal':
            time = float(self.road.get_exec_time())
            if time != 0:
                for lane in data:
                    laneresult.append(round(lane/time, PREC))
                whole = round(sum(data)/time, PREC)
            else:
                laneresult = [0]*len(data)
                whole = 0
            
        elif self.method == 'head':
            headt = self.road.get_head_t()
            sumt = 0
            sumcar = 0
            for t in headt:
                time = float(sum(t))
                if time != 0:
                    num = len(t)+1
                    laneresult.append(round(num/time, PREC))
                    sumt += time
                    sumcar += num
                else:
                    laneresult.append(0)
            if sumt != 0:
                whole = round(sumcar/sumt, PREC)
            else:
                whole = 0
        else:
            raise KeyError('No such method')
        return laneresult, whole
        
    def get_density(self):
        meanv, whole_d = self.road.get_mean_speed()
        meanflux, whole_f = self.get_flux()
        output = []
        for i in xrange(len(meanv)):
            if meanv[i] != -1 and meanv[i] != 0:
                output.append(round(meanflux[i]/meanv[i], PREC))
            else:
                output.append(0)
        if whole_d != None:
            whole = round(whole_f/whole_d, PREC)
        else:
            whole = 0
        
        return output, whole
            

    def get_occupancy(self):
        pass
