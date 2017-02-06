#!/usr/bin/env python
# coding=utf-8
import numpy as np
import basicplot as bp
import road 
import pandas as pd
import copy 
plantime = 10
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
InitCar = road.initCarsDistributed(
    50, [carTemp, carTemp2], lanes = 3, pers = [0.5, 0.5])
EmptyCar = road.initEmptyRoad(lanes = 3)


if __name__ == '__main__':


    print 'Process start'
    rd0 = road.execRoad(InitCar, vmax, 100, enterflag=True, lanes=3)
    rd1 = road.execRoad(EmptyCar, vmax, 500, lanes=3)
    rd0.setConnectTo(rd1)
    rd = road.execRoad(copy.deepcopy(EmptyCar), vmax, 500, lanes=3)
    rd1.setConnectTo(rd)
    
    #rd0.setConnectTo(rd1)
    #rd1.setConnectTo(rd, 1000)
    

    #rd.cycleBoundaryCondition(True, [carTemp, carTemp2], pers = [0.5, 0.5])
    #rd0.timeBoundaryCondition(True, [carTemp], timeStep=5)

    #bp.addRoad(np.array([0.0, 100.0]), np.array([50.0, 50.0]), [rd0, rd1, rd])
    #bp.plot()


    '''
    for i in xrange(0,plantime):
        print i,'s'
        for road in [rd0, rd1, rd]:
            print road.get_cars_v()
            road.reflush_status()
    '''
    
    print 'Done'
