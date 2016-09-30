#!/usr/bin/env python
# coding=utf-8

import basicroad as br
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

class BasicLayer(object): 
    '最底层图层设置'
    def __init__(self, initSize_ = 14, initColor_ = 'black',xlim_=[0, 100], ylim_=[0, 100]):
        self.fig = plt.figure(figsize=(initSize_, initSize_), facecolor = initColor_)
        self.ax = self.fig.add_axes([0, 0, 1, 1], frameon = False)
        self.ax.set_xlim(xlim_)
        self.ax.set_ylim(ylim_)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
    def getLayer(self):
        return self.fig     
    def getScatLayer(self):
        return self.ax

class RoadPlot(object):
    '绘制直线跑道'
    def __init__(self, rX_, rY_, road_, plotLayer_, width_ = 1):
        self.rX = rX_                                                   #道路起点和终点的X坐标
        self.rY = rY_                                                   #道路起点和终点的Y坐标
        self.width = width_                                             #道路宽度的绘图倍数
        self.road = road_                                               #指向要绘出的道路    
        self.plotLayer = plotLayer_                                     #指向要绘画的图层
        self.scat = self.plotLayer.scatter([0], [0], s = 1)             
        

    def plot(self, color_ = False, reflush_ = True):
        if reflush_:   
            #self.road = road_                                               #更新要显示车道的信息
            self.scat.set_offsets(self.getPlotInfo()) 
            if color_:                                                      #如果color_为True,则会根据车辆的当前速度与最大速度为其绘制颜色        
                self.scat.set_edgecolors(self.getColorMap())
            self.road.reflushStatus() 
        else:
            pass

    def setPlot(self):
        #MAX_VAULE = 670
        #WIDTH --> Y : 6.25 --> 1  WIDTH --> X : 10 --> 1

        roadWidth = 100
        mappingY = 6.25
        mappingX = 10
        lanes = self.road.getRoadLanes()
        laneWidth = roadWidth/lanes
        thetaX = 1-((self.rX[1] - self.rX[0]) /np.sqrt( np.power(self.rX[0] - self.rX[1],2) + np.power(self.rY[0] - self.rY[1], 2))  )
        thetaY = np.sqrt(1-np.power(thetaX, 2))

        offsetX = ((roadWidth*thetaX/2)/mappingX)
        offsetY = ((roadWidth*thetaY/2)/mappingY)

        self.plotLayer.plot(self.rX, self.rY, 'w', linewidth=roadWidth, alpha=0.3)     #绘出道路
        #绘制道路边界
        self.plotLayer.plot(np.array(self.rX)+offsetX, np.array(self.rY)+offsetY, 'b', linewidth=1, alpha=0.6)    
        self.plotLayer.plot(np.array(self.rX)-offsetX, np.array(self.rY)-offsetY, 'b', linewidth=1, alpha=0.6)
        #绘制车道
        for i in xrange(1,lanes+1):
             self.plotLayer.plot()
    
    def getColorMap(self):
        collector = []
        vmax = self.road.getRoadVMax()
        vBox = self.road.getCarsV()
        for laneV in vBox:
            for v in laneV:
                if v <= 0.2*vmax:
                    collector.append([1., 0., 0., 1.])
                elif v <= 0.6*vmax:
                    collector.append([1., 1., 0., 1.])
                else:
                    collector.append([0., 1., 0., 1.])
        return np.array(collector)
    
    #TODO:多车道映射未作
    def getPlotInfo(self):
        output = np.array([])

        #---temp test
        index = 0
        #---
        for locate in self.road.getCarsLocate():
            mapping = locate/self.road.getRoadLength()                 #映射比率值
            plotX = mapping*((self.rX[1] - self.rX[0]))+self.rX[0]
            #---
            plotY = mapping*((self.rY[1] - self.rY[0]))+self.rY[0]+index*5
            #---
            output = np.append(output, np.array((plotX,plotY)).T)
            index += 1
        return output

#-----------------------------------------------------------------------------
'绘制动画'
layer = BasicLayer()
roadList = []
    
def addRoad(xlim_, ylim_, road_):
    temp = RoadPlot(xlim_, ylim_, road_, layer.getScatLayer())
    temp.setPlot()
    roadList.append(temp)       
    
def update(frame_number):
    for road in roadList:
        road.plot(color_ = True)    
    
def plot():
    'Waring: Cannot stop this,once started'
    animation = FuncAnimation(layer.getLayer(), update, interval = 10)
    plt.show()
#----------------------------------------------------------------------------
