#!/usr/bin/env python
# coding=utf-8
import numpy as np
import basicroad as br
#import basicplot as bp
import statistics as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from matplotlib import cm
import pandas as pd
plantime = 50
carsNum = 10
vmax = 20
carTemp = br.Car()
carTemp.vDistance = 5
carTemp.length = 5
InitCar = br.initCarsDistributed(
    2000, carTemp, [vmax*0.8] * carsNum, carsNum, lanes = 1)
if __name__ == '__main__':
    
    
    print 'Process start'
    
    '''
    rd = br.MCDRoad(InitCar, vmax, 2000, enterFlag_=True, lanes_=1)
    #rd2 = br.Road(br.initEmptyRoad(2), vmax, 500, lanes_=2)
    #rd.setConnectTo(rd2)
    rd.addCarAutomaticByTime(True, carTemp, 2)
    #rd.addCarAutomaticByBound(True, carTemp)
    #bp.addRoad(np.array([20.0, 70.0]), np.array([50.0, 50.0]), rd)
    #bp.plot()

    
    #rd.setTT(True)
    rdinfo = br.ProcessWriter(rd,'road2',plantime)
    rdinfo.setInit()
    for i in xrange(0,plantime):
        rd.reflushStatus()
        rdinfo.writeInfo()
    rdinfo.cleanAll()
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111, projection = '3d')
    
    vData = []
    locateData = []
    time = []
    rd = br.MCDRoad(InitCar, vmax, 2000, enterFlag_ = True, lanes_ = 1)
    #rd.addCarAutomaticByBound(True, carTemp)
    for i in xrange(plantime):
        rd.reflushStatus()
        cars = rd.getCarsInfo()[0]
        for o in xrange(len(cars)):
            vData.append(cars[o].v)
            locateData.append(cars[o].locate)
            time.append(i)
    df = pd.DataFrame([])
    df['Time'] = time
    df['Locate'] = locateData
    df['V'] = vData
    df.to_excel(r'./data.xlsx')
    #time, locateData = np.meshgrid(time, locateData)
    #ax.plot_surface(time, locateData, vData)
    print 'Done'
    
