#!/usr/bin/env python
# coding=utf-8
import numpy as np
#import basicplot as bp
import road 
import pandas as pd
import copy 
import statistics as ss
import plot
plantime = 6000
carsNum = 30
vmax = 5
carTemp = road.Car()
carTemp.safedistance = 0
carTemp.length = 1
carTemp.speed = vmax

carTemp2 = road.Car()
carTemp2.name = 'no'
carTemp2.safedistance = 5
carTemp2.length = 3
carTemp2.speed = 0.5*vmax
InitCar = road.init_cars_distributed(
    2000, [carTemp, carTemp2], lanes = 3, pers = [0.5, 0.5])
EmptyCar = road.init_empty_road(lanes = 3)
EmptyCar2 = road.init_empty_road(lanes = 4)

if __name__ == '__main__':


    print 'Process start'
    rd = road.ExecRoad(InitCar, vmax, 2000, enterflag=True, lanes=3)
    #rd1 = road.ExecRoad(EmptyCar, vmax, 2000, enterflag=True, lanes=3)
    #rd.set_connect_to(rd1)
    #rds = ss.RoadStatus(rd, 'head')
    

    #rd.cycle_boundary_condition(True, [carTemp, carTemp2], pers = [0.5, 0.5])
    rd.time_boundary_condition(True, [carTemp], timeStep=60, nums=3)
    '''
    for i in xrange(plantime):
        rd.reflush_status()
        rd1.reflush_status()
        print rd1.get_cars_v()[0]
        print '---------------'
        print rd1.get_mean_speed()
    '''
    #ss.road_runner([rd], plantime, './test.xlsx', timestep='min')
    
    plot.read_data('./test.xlsx', 'SummaryData', 0, '0x7f7b07ac3d50')

    print 'Done'
