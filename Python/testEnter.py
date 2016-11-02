#!/usr/bin/env python
# coding=utf-8
import numpy as np
import basicroad as br
import basicplot as bp
import statistics as st
plantime = 300
carsNum = 100
vmax = 5
carTemp = br.Car()
carTemp.vDistance = 0
carTemp.length = 1
InitCar = br.initCarsDistributed(
    500, carTemp, [0] * carsNum, carsNum, lanes = 1)
if __name__ == '__main__':
    
    print 'Process start'
    rd = br.NSRoad(InitCar, vmax, 1000, enterFlag_=True, lanes_=1)
    #rd2 = br.Road(br.initEmptyRoad(2), vmax, 500, lanes_=2)
    #rd.setConnectTo(rd2)
    #rd.addCarAutomaticByTime(True, carTemp, 2)
    #rd.addCarAutomaticByBound(True, carTemp)
    #rd.setTT(True)
    rdinfo = br.ProcessWriter(rd,'road2',plantime)
    rdinfo.setInit()
    counter = 0
    for i in xrange(0,plantime):
        counter += 1
        if counter >= 10000:
            print i*100.0/plantime,'%'
            counter = 0
        rd.reflushStatus()
        rdinfo.writeInfo()
    rdinfo.cleanAll()
    print 'Done'
    
