#!/usr/bin/env python
# coding=utf-8
import numpy as np
import basicplot as bp
import road 
import pandas as pd
import copy 
import statistics as ss
plantime = 5000
carsNum = 30
vmax = 20.0
carTemp = road.Car()
carTemp.safedistance = 5
carTemp.length = 4
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
    rds = ss.RoadStatus(rd, 'head')
    

    #rd.cycle_boundary_condition(True, [carTemp, carTemp2], pers = [0.5, 0.5])
    rd.time_boundary_condition(True, [carTemp], timeStep=1, nums=3)

    #bp.addRoad(np.array([0.0, 100.0]), np.array([50.0, 50.0]), [rd, rd1, rd0])
    #bp.plot()


    
    for i in xrange(0,plantime):
        print rds.get_flux()
        rd.reflush_status()
    
    
    print 'Done'
