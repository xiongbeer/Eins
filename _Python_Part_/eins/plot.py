import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

def plot(path, oplane, roadid, savepath=None):
    data = pd.read_excel(path, 'SpaceTimeData')
    data = data[data['LANE_ID'] == oplane]
    data =  data[data['ROAD_HASH_ID'] == roadid]
    y, x = get_space_time_data(data)
    plt.scatter(x, y, c='k', alpha=0.2, s=1)

def get_space_time_data(data):
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