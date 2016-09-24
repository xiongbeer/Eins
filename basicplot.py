#!/usr/bin/env python
# coding=utf-8

import basicroad as br
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

def update(frame_number):
    x = rd.getCarsLocate()[0]
    y = [1]*x.size

    scat.set_offsets(np.array((x,y)).T)
    rd.reflushStatus()
    print frame_number
vmax = 16.7

locateInit = br.initCarsDistributed(100, 50)
vBoxInit = np.array([0.5*vmax]*locateInit.size)
rd = br.Road([locateInit], [vBoxInit], vmax, 1000, enterFlag_ = True, frames_ = 1)
rd.evenAddAutomaticVehicleSwitch(True, 0.5*vmax)

fig = plt.figure(figsize=(14, 14))
ax = fig.add_axes([0, 0, 1, 1], frameon=False)
ax.set_xlim(0, 1000), ax.set_xticks([])
ax.set_ylim(0, 2), ax.set_yticks([])
x = rd.getCarsLocate()[0]
scat = ax.scatter(x, [1]*x.size,
                  s=200, lw=0.5, facecolors='none')

animation = FuncAnimation(fig, update, interval=10)
plt.show()
