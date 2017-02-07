#!/usr/bin/env python
# coding=utf-8
import numpy as np
import road as rd
import pandas as pd

def road_runner(roadbox, exectime):
    for i in xrange(exectime):
        for road in roadbox:
            road.reflush_status()

class RoadStatus(object):
    def __init__(self, road):
        self.road = road
        self.timer = 0
        self.dataset = pd.DataFrame()

    def get_flux(self, method='normal'):
        data = self.road.get_leave_cars()
        laneresult = []
        if method == 'normal':
            time = self.road.get_exec_time()

            if time != 0:
                for lane in data:
                    laneresult.append(lane/time)
                whole = sum(data)/time
            else:
                laneresult = [0]*len(data)
                whole = 0
            
        elif method == 'head':
            headt = self.road.get_head_t()
            sumt = 0
            sumcar = 0
            for t in headt:
                time = sum(t)
                if time != 0:
                    num = len(t)+1
                    laneresult.append(time/num)
                    sumt += time
                    sumcar += num
                else:
                    laneresult.append(0)
            if sumt != 0:
                whole = sumcar/sumt
            else:
                whole = 0

        return laneresult, whole
        
    def get_density(self, method='normal'):
        meanv, whole_d = self.road.get_mean_speed()
        meanflux, whole_f = self.get_flux(method)
        output = []
        for i in xrange(len(meanv)):
            if meanv[i] != -1 and meanv[i] != 0:
                output.append(meanflux[i]/meanv[i])
            else:
                output.append(0)
        if whole_d != None:
            whole = whole_f/whole_d
        else:
            whole = 0
        
        return output, whole
            

    def get_occupancy(self):
        pass
    
    def get_headway(self):
        pass