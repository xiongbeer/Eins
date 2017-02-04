#!/usr/bin/env python
# coding=utf-8
import numpy as np
import basicroad as br
import basicplot as bp
import road
import statistics as st
import pandas as pd
plantime = 50
carsNum = 30
vmax = 20
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
    100, [carTemp, carTemp2], lanes = 3, pers = [0.5, 0.5])
EmptyCar = road.initEmptyRoad(lanes = 3)
if __name__ == '__main__':


    print 'Process start'

    rd = road.execRoad(InitCar, vmax, 2000, enterflag=True, lanes=3)
    rd.set_exec_rule('A')
    #rd2 = br.Road(br.initEmptyRoad(2), vmax, 500, lanes_=2)
    #rd.setConnectTo(rd2)
    #rd.cycleBoundaryCondition(True, [carTemp, carTemp2], pers = [0.5, 0.5])
    rd.timeBoundaryCondition(True, [carTemp, carTemp2], pers = [0.5, 0.5])
    #rd.addCarAutomaticByBound(True, carTemp)

    #bp.addRoad(np.array([0.0, 100.0]), np.array([50.0, 50.0]), rd)
    #bp.plot()


    '''
    #rd.setTT(True)
    rdinfo = br.ProcessWriter(rd,'road2',plantime)
    rdinfo.setInit()
    for i in xrange(0,plantime):
        rd.reflushStatus()
        rdinfo.writeInfo()
    rdinfo.cleanAll()
    '''
    print 'Done'
