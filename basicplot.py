#!/usr/bin/env python
# coding=utf-8

import basicroad as br
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation


#绘直线跑道
class RoadPlot(object):
    def __init__(self, rX_, rY_, road_, plotLayer_, laneWidth_ = 1):
        self.rX = rX_                                                   #道路起点和终点的X坐标
        self.rY = rY_                                                   #道路起点和终点的Y坐标
        self.laneWidth = laneWidth_                                     #道路宽度的绘图倍数
        self.road = road_                                               #指向要绘出的道路    
        self.plotLayer = plotLayer_                                     #指向要绘画的车道
        self.speedColorOn = True                                        #
    def updateInfo(self, road_):                                        #更新要显示车道的信息
        self.road = road_
    def setPlot(self):
        self.plotLayer.plot(self.rX, self.rY, 'w',linewidth=100, alpha=0.3)     #绘出车道
    
    #TODO:根据车速设置车辆颜色
    def setColorLaw(self):
        pass
    def getColorMap(self):
        pass
    
    #TODO:多车道映射未作
    def getPlotInfo(self):
        output = []
        for locate in self.road.getCarsLocate():
            mapping = locate/self.road.getRoadLength()                 #映射比率值
            plotX = mapping*((self.rX[1] - self.rX[0]))+self.rX[0]
            plotY = mapping*((self.rY[1] - self.rY[0]))+self.rY[0]
            output.append(np.array((plotX,plotY)).T)
        
        return output

def update(frame_number):
    rd_p.updateInfo(rd)
    showData = np.array([])
    for position in rd_p.getPlotInfo():
        showData = np.append(showData, position)
    for position in rd_p2.getPlotInfo():
        showData = np.append(showData, position)
    scat.set_offsets(showData)
    rd.reflushStatus()
    rd2.reflushStatus()
vmax = 16.7

locateInit = br.initCarsDistributed(100, 40)
vBoxInit = np.array([0.5*vmax]*locateInit.size)
locateEmpty = np.array([-1])
vBoxEmpty = np.array([0])

rd = br.Road([locateInit], [vBoxInit], vmax, 1000, enterFlag_ = True, frames_ = 1)
rd.evenAddAutomaticVehicleSwitch(True, 0.5*vmax)

rd2 = br.Road([locateEmpty], [vBoxEmpty], vmax, 500)

rd.setConnectTo(rd2)

fig = plt.figure(figsize=(14, 14))
ax = fig.add_axes([0, 0, 1, 1], frameon=False)
ax.set_xlim(0, 100), ax.set_xticks([])
ax.set_ylim(0, 100), ax.set_yticks([])

x = rd.getCarsLocate()[0]
rd_p = RoadPlot(np.array([0, 50]), np.array([80, 80]), rd, ax)
rd_p.setPlot()

rd_p2 = RoadPlot(np.array([50, 50]), np.array([80, 40]), rd2, ax)
rd_p2.setPlot()

scat = ax.scatter(x, [1]*x.size,
                  s=200, lw=0.5, facecolors='none')

animation = FuncAnimation(fig, update, interval=10)
plt.show()
