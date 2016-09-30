#!/usr/bin/env python
# coding=utf-8
import numpy as np
import basicroad as br
import basicplot as bp

vmax = 16.7
locateInit, vBoxInit = br.initCarsDistributed(500, 100, 0.5*vmax)
if __name__ == '__main__':
    rd = br.Road([locateInit], [vBoxInit], vmax, 2000, view_=150, enterFlag_ = True)
    rd.evenAddAutomaticVehicleSwitch(True, 0.5*vmax)
    bp.addRoad(np.array([20, 70]), np.array([50, 50]), rd)
    bp.plot()
