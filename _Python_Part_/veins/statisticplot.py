#!/usr/bin/env python
# coding=utf-8
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

#读取数据
class DataParse(object):
    def __init__(self, dataPath):
        self.dataSet = pd.read_csv(dataPath, sep=' ', iterator=True)
        reader = self.dataSet.get_chunk(1)
        self.lanes = reader['Locate'][0]
        self.plantime = reader['Time'][0]
        self.roadLength = reader['V'][0]
        self.tempData = None
        self.buffer = 0
    def parseVBox(self):
        pass
    
    def parseLocateInfo(self):
        output = []
        timeMap = []
         
        time = self.tempData['Time'][self.buffer]
        for i in self.tempData['Locate'].str.split(':')[self.buffer]:
            temp = np.array(i.split(','), dtype='float')
            output.append(temp)
            timeMap.append(np.array([self.plantime - time]*temp.size))
        return output,timeMap
    
    def getPlanTime(self):
        return self.plantime
    
    def getRoadLength(self):
        return self.roadLength

    def readNextLine(self):
        self.buffer += 1
        self.tempData = self.dataSet.get_chunk(1)

    def getRoadLanes(self):
        return self.lanes

#图层
class Layer(object):
    def __init__(self, lanes, planTime_ = 0, roadLength_ = 0, initsize_ = 14, plotModel_ = 'default'):
        self.fig = plt.figure(figsize = (initsize_, initsize_))
        self.plotModel = plotModel_
        self.planTime = planTime_
        self.roadLength = roadLength_

    def savePicture(self, outputName_):
        self.fig.savefig(outputName_ + '.jpg')

    def getLayer(self):
        return self.ax
    
    def setTimeAndLength(self, time_, length_):
       self.planTime = time_
       self.roadLength = length_

    def getPlotModel(self):
        return self.plotModel

    #选择不同的模式绘图设置需要改变
    def setModel(self):
        if self.plotModel == 'default':
            self.ax = self.fig.add_subplot(1,1,1)
            self.ax.set_xlabel('\nSpace          --------->')
            self.ax.set_ylabel('<----------          Time\n')
            self.ax.set_xticks([])
            self.ax.set_yticks([])
        elif self.plotModel == 'detail':
            self.ax = self.fig.add_subplot(1,1,1)
            self.ax.set_ylabel('x / ft')
            self.ax.set_xlabel('t / s')
            self.ax.set_xlim([0, self.planTime])
            self.ax.set_ylim([0, self.roadLength])
        else:
            raise KeyError('Unknow Plot Model')

#时空图绘制
class TXPlot(object):
    def __init__(self, dataPath_, outputName_, layer_ = None):
        self.plotLayer = layer_
        self.dataPath = dataPath_
        self.parser = DataParse(dataPath_)
        self.outputName = outputName_ 
        self.planTime = self.parser.getPlanTime()
        self.roadLength = self.parser.getRoadLength() 

    def resetLayer(self, layer_):
        self.plotLayer = layer_
        self.plotModel = self.plotLayer.getPlotModel()
        self.plotLayer.setTimeAndLength(self.planTime, self.roadLength)
        self.plotLayer.setModel()

    def plot(self):
        flag = True
        while(flag == True):
            try:
                self.parser.readNextLine()
                x,y = self.parser.parseLocateInfo()
                if self.plotModel == 'detail':
                    y = self.planTime - y
                    x,y = y,x
                self.plotLayer.getLayer().scatter(x[0], y[0], s = 0.1)
            except StopIteration:
                flag = False
        self.plotLayer.savePicture(self.outputName)
        print 'Done'

#测试用
if __name__ == '__main__':
    A = Layer(1)
    B =  TXPlot(r'./ProcessInfo_road2.csv', 'demo2')
    B.resetLayer(A)
    B.plot()
