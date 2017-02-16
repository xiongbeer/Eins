#!/usr/bin/env python
# coding=utf-8
from __future__ import division
import pandas as pd
import numpy as np
import copy
import _tips
from tqdm import tqdm, trange

KEY = {'ROAD_HASH_ID':[],'LANE_ID':[],'TIME_STAMP':[],'AVR_SPEED':[],'FLUX':[],'DENSITY':[],'CARS_NUM':[],'LEAVE_CARS':[]}
PREC =  3   # 精度
def road_runner(roadbox, exectime, savepath, timestep='sec', st=True, sm=True, bar=True, ownfun=None):
    print _tips.INFO('Process start...', 'GREEN')

    if ownfun != None and bar is False:
            raise ValueError(_tips.INFO("ownfun isn't None while bar is False", 'RED'))

    if bar is True:
        loop = trange(exectime)
        info_d = loop.set_description
        info_p = loop.set_postfix
        info_r = loop.refresh
        info_w = loop.write
    else:
        loop = range(exectime)
        info_d = __empty
        info_p = __empty
        info_r = __empty
        info_w = __empty

    roadstbox = []
    summarydata = pd.DataFrame(KEY)
    tsdata = pd.DataFrame({'ROAD_HASH_ID':[], 'LANE_ID':[], 'TIME_STAMP':[], 'LOCATE':[]})
    writer = pd.ExcelWriter(savepath+'.xlsx')
    for road in roadbox:
        rds = RoadStatus(road,timestep=timestep)
        roadstbox.append(rds)

    info_p(stdata=str(st), summarydata=str(sm))
    info_d(_tips.INFO('Collecting data', 'GREEN'))
    for i in loop:
        try:
            for road in roadbox:
                road.reflush_status()
            for stat in roadstbox:
                if sm is True:
                    temp = stat.summary()
                    if len(temp) != 0:
                        summarydata = summarydata.append(temp)
                if st is True:
                    temp = stat.get_time_space()
                    tsdata = tsdata.append(temp)
            if ownfun is not None:
                info_w(ownfun())
        except:
            info_d(_tips.INFO('FAILED!', 'RED'))
            info_r()
            raise KeyError
    print _tips.INFO('Start writing data...', 'BLUE')
    summarydata.to_excel(writer, 'SummaryData', index=False)
    tsdata.to_excel(writer, 'SpaceTimeData', index=False)
    writer.save()
    print _tips.INFO('Done', 'GREEN')

def __empty(*args, **kwargs):
    pass
class RoadStatus(object):
    def __init__(self, road, method='normal', timestep='sec'):
        self.road = road
        self.dataset = pd.DataFrame()
        self.method = method
        self.timecounter = 1
        self.lanes = road.get_road_lanes()
        self.perwhole = {'denisty':0.0, 'flux':0.0}
        self.perlanedata = {'denisty':np.zeros(road.get_road_lanes()), 'flux':np.zeros(road.get_road_lanes())}
        self.hashid = hex(id(road))
        self.SPEED= []
        for i in xrange(self.lanes+1):
            self.SPEED.append([])
        if timestep == 'sec':
            self.timestep = 1
        elif timestep == 'min':
            self.timestep = 60
        elif timestep == 'hour':
            self.timestep = 60*60
        else:
            raise KeyError('No such method')

    def __timer(self):
        if self.timecounter != self.timestep:
            self.timecounter += 1
            return True
        else:
            self.timecounter = 1
            return False

    def get_time_space(self):
        df = pd.DataFrame({'ROAD_HASH_ID':[], 'LANE_ID':[], 'TIME_STAMP':[], 'LOCATE':[]})
        LOCATE = []
        locatedata = self.road.get_cars_locate()
        for i in xrange(self.lanes):
            LOCATE.append(locatedata[i])
        df['LOCATE'] = LOCATE
        df['ROAD_HASH_ID'] = [self.hashid]*self.lanes
        df['LANE_ID'] = range(self.lanes)
        df['TIME_STAMP'] = [self.road.get_exec_time()]*self.lanes
        return df

    def summary(self):
        AVRSPEED= []
        HASHID = []
        LANENUMBER = []
        TIMESTAMP = []
        FLUX = []
        DENSITY = []
        CARSNUM = []
        LEAVECARS = []
        data_leave = self.road.get_leave_cars()
        data_speed = self.road.get_mean_speed()
        data_num = self.road.get_cars_num()
        output = pd.DataFrame(KEY)

        # 速度需要手动累加
        for i in xrange(self.lanes):
            if data_speed[0][i] != -1:
                self.SPEED[i].append(data_speed[0][i])
        if data_speed[1] != None:
            self.SPEED[self.lanes].append(data_speed[1])

        if self.__timer():
            pass
        else:
            time = self.road.get_exec_time()
            HASHID.append(self.hashid)
            LANENUMBER.append(-1)
            TIMESTAMP.append(time)
            if len(self.SPEED[self.lanes]) != 0:
                speed = sum(self.SPEED[self.lanes])/len(self.SPEED[self.lanes])
                AVRSPEED.append(speed)
            else:
                speed = ' '
                AVRSPEED.append(speed)

            flux = sum(data_leave) - self.perwhole['flux']
            FLUX.append(flux)
            if speed != ' ' and speed != 0:
                DENSITY.append(flux/speed)
            else:
                DENSITY.append(' ')

            CARSNUM.append(sum(data_num))
            LEAVECARS.append(sum(data_leave))
            for i in xrange(self.lanes):
                HASHID.append(self.hashid)
                LANENUMBER.append(i)
                TIMESTAMP.append(time)
                if len(self.SPEED[i]) != 0:
                    speed = sum(self.SPEED[i])/len(self.SPEED[i])
                    AVRSPEED.append(speed)
                else:
                    speed = ' '
                    AVRSPEED.append(speed)
                flux = data_leave[i] - self.perlanedata['flux'][i]
                FLUX.append(flux)
                if speed != ' ' and speed != 0:
                    DENSITY.append(flux/speed)
                else:
                    DENSITY.append(' ')
                CARSNUM.append(data_num[i])
                LEAVECARS.append(data_leave[i])
            self.perlanedata['flux'] = copy.deepcopy(data_leave)
            self.perwhole['flux'] = sum(data_leave)
            output['ROAD_HASH_ID'] = HASHID
            output['LANE_ID'] = LANENUMBER
            output['TIME_STAMP'] = TIMESTAMP
            output['AVR_SPEED'] = AVRSPEED
            output['FLUX'] = FLUX
            output['DENSITY'] = DENSITY
            output['CARS_NUM'] = CARSNUM
            output['LEAVE_CARS'] = LEAVECARS
            # 清空之前存储的速度累加数据
            self.SPEED= []
            for i in xrange(self.lanes+1):
                self.SPEED.append([])
        return output
