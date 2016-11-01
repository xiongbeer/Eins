#!/usr/bin/env python
# coding=utf-8
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

class DataParse(object):
    def __init__(self, dataPath):
        self.dataSet = pd.read_csv(dataPath, sep=' ', iterator=True)
        reader = self.dataSet.get_chunk(1)
        self.lanes = reader['Locate'][0]
        self.plantime = reader['Time'][0]
        self.tempData = None
        self.buffer = 0
    def parseVBox(self):
        pass
    
    def parseLocateInfo(self):
        output = []
        timeMap = []
        
        time = self.tempData['Time'][self.buffer]
        for i in self.tempData['Locate'].str.split(':')[self.buffer]:
            temp = np.array(i.split(','),dtype='float')
            output.append(temp)
            timeMap.append(np.array([self.plantime-time]*temp.size))
        return output,timeMap
    
    def readNextLine(self):
        self.buffer += 1
        self.tempData = self.dataSet.get_chunk(1)

    def getRoadLanes(self):
        return self.lanes

class Layer(object):
    def __init__(self, lanes, initsize_ = 14):
        self.fig = plt.figure(figsize=(initsize_, initsize_))
        self.ax = self.fig.add_subplot(1,1,1)
        self.ax.set_xlabel('\nSpace          ---------->')
        self.ax.set_ylabel('<----------          Time\n')
        self.ax.set_xticks([])
        self.ax.set_yticks([])
    
    def savePicture(self, outputName_):
        self.fig.savefig(outputName_+'.jpg')

    def getLayer(self):
        return self.ax

class TXPlot(object):
    def __init__(self, layer_, dataPath_, outputName_):
        self.plotLayer = layer_
        self.dataPath = dataPath_
        self.parser = DataParse(dataPath_)
        self.outputName = outputName_
    
    def plot(self):
        flag = True
        while(flag == True):
            try:
                self.parser.readNextLine()
                x,y = self.parser.parseLocateInfo()
                self.plotLayer.getLayer().scatter(x[0], y[0], s = 0.1)
            except StopIteration:
                flag = False
        self.plotLayer.savePicture(self.outputName)
        print 'Done'


if __name__ == '__main__':
    A = Layer(1)
    B =  TXPlot(A,  r'./ProcessInfo_road2.csv', 'demo2')
    B.plot()
