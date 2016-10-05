#!/usr/bin/env python
# coding=utf-8
import numpy as np
import basicroad as br
import basicplot as bp
import statistics as st
carsNum = 100
vmax = 16.7
carTemp = br.Car()
carTemp.v = vmax * 0.5
InitCar = br.initCarsDistributed(1000, carTemp, [vmax * 0.5] * carsNum, carsNum, lanes=2)
if __name__ == '__main__':
    rd = br.Road(InitCar, vmax, 1000, enterFlag_=True, lanes_=2)
    rd2 = br.Road(br.initEmptyRoad(2), vmax, 500, lanes_=2)
    rd.setConnectTo(rd2)
    rd.addCarAutomaticByTime(True, carTemp, 2)
    bp.addRoad(np.array([0, 50]), np.array([50, 50]), rd)
    bp.addRoad(np.array([60, 90]), np.array([50, 50]), rd2)
    bp.plot()
