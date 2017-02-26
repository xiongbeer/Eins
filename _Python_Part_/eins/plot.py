import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

def plot(path, oplane, roadid, savepath):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    data = pd.read_excel(path+'.xlsx', 'SpaceTimeData')
    data = data[data['LANE_ID'] == oplane]
    data =  data[data['ROAD_HASH_ID'] == roadid]
    y, x = __get_space_time_data(data)
    layer = ax.scatter(x, y, c='k', alpha=0.2, s=0.1, marker='x')
    plt.savefig(savepath, dpi=1000)
    return layer

def __get_space_time_data(data):
    locate = []
    time = []
    row, col = data.shape
    for i in xrange(row):
        t = data['TIME_STAMP'].iloc[i]
        for word in data['LOCATE'].iloc[i].split(' '):
            try:
                locate.append(float(word))
                time.append(t)
            except:
                pass
    return time, locate
