#!/usr/bin/env python
# coding=utf-8
import numpy as np
import basicroad as br
import basicplot as bp
import statistics as st
carsNum = 50
vmax = 16.7
carTemp = br.Car()
carTemp.v = vmax*0.5
InitCar = br.initCarsDistributed(500, carTemp, [vmax*0.5]*carsNum, carsNum, lanes=1)
if __name__ == '__main__':
    rd = br.Road(InitCar, vmax, 2000, enterFlag_ = True, lanes_=1)
    rd.evenAddAutomaticVehicleSwitch(True, carTemp)
    
    #rd.addCarAutomaticByTime(True, carTemp, 2)
    rd_st = st.RoadStatus(rd, timeStep_ = 'min')
    for i in xrange(1000):
        rd.reflushStatus()
        info = rd_st.meanTrafficVolume()
        if info != -1:
            print info.sum()
    #bp.addRoad(np.array([20, 70]), np.array([50, 50]), rd)
    #bp.plot()

