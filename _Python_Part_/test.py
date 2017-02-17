#!/usr/bin/env python
# coding=utf-8
from eins import road
from eins import statistics
import copy

if __name__ == '__main__':
    # some paras
    length = 1000
    exectime = 100
    lanes = 3
    vmxa = 6

    # define cars
    car = road.Car()
    car1 = road.Car()
    car.name = 'No1'
    car1.name = 'No2'
    car.acc = 2.0

    # get init box
    carbox = road.init_cars_distributed(length, [car, car1], pers=[0.3, 0.7], lanes=lanes)
    emptybox = road.init_empty_road(lanes)

    # get road
    rd = road.ExecRoad(length, carbox, vmax, lanes)
    rd1 = road.ExecRoad(length, emptybox, vmax, lanes)
    rd2 = road.ExecRoad(length, copy.deepcopy(emptybox), vmax, lanes)

    # define re
    rd.set_connect_to(rd1)
    rd1.set_connect_to(rd2, 0.5*length)

    rd.cycle_boundary_condition(True, [car, car1], pers=[0.3, 0.7])
