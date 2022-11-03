# main.py

import argparse
import csv
import json
import logging
import math
import os
import random
# from chase.sheep import Sheep
# from chase.wolf import Wolf
from configparser import ConfigParser


class Wolf:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Sheep:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dist = 0.0
        self.status = "alive"
        self.no = 0

    def move(self, sheep_move_dist):
        direction = random.randint(1, 4)
        if direction == 1:
            self.y += sheep_move_dist
        elif direction == 2:
            self.x += sheep_move_dist
        elif direction == 3:
            self.y -= sheep_move_dist
        else:
            self.x -= sheep_move_dist


def setup(sheep_no, init_pos_limit):
    sheep = []
    for i in range(sheep_no):
        sheep.append(Sheep(random.uniform(-init_pos_limit, init_pos_limit),
                           random.uniform(-init_pos_limit, init_pos_limit)))
        sheep[i].no = i
    log = "setup(" + str(sheep_no) + str(init_pos_limit) + ") called, returned" + str(sheep)
    logging.debug(log)
    return sheep


def euclidean(sheep, wolf):
    euclidean_distance = math.sqrt(((sheep.x - wolf.x) ** 2) + ((sheep.y - wolf.y) ** 2))
    log = "euclidean(" + sheep.__str__() + wolf.__str__() + ") called, returned" + str(euclidean_distance)
    logging.debug(log)
    return euclidean_distance


def wolf_move(wolf_move_dist, nearest, wolf):
    log = "wolf_move(" + str(wolf_move_dist) + nearest.__str__() + wolf.__str__() + ") called"
    logging.debug(log)
    x_an = wolf_move_dist * ((nearest.x - wolf.x) / nearest.dist)
    y_an = wolf_move_dist * ((nearest.y - wolf.y) / nearest.dist)
    wolf.x += x_an
    wolf.y += y_an


def json_export(sheep, wolf, round_no, directory):
    # if not directory:
    #     directory = "None"
    # log = "json_export(" + sheep.__str__() + wolf.__str__() + round_no.__str__() + directory, ") called"
    # logging.debug(log)
    x = {
        "round_no": round_no,
        "wolf_pos": str(wolf.x) + ", " + str(wolf.y)
    }
    pos = []
    for i in sheep:
        if i.status == "alive":
            pos.append(str(i.x) + ", " + str(i.y))
        else:
            pos.append("None")
    x['sheep_pos'] = pos
    if round_no == 1:
        if directory:
            direct = os.getcwd()
            path = direct + '\\' + directory
            dir_path = os.path.dirname(path)
            if not os.path.exists(dir_path):
                print("Create")
                os.mkdir(directory)
            os.chdir(directory)
        f = open("pos.json", "w")
    else:
        f = open("pos.json", "a")
    f.write(json.dumps(x, indent=4, sort_keys=True))
    f.close()


def csv_export(round_no, sheep_no):
    # logging.debug("csv_export(", round_no, sheep_no, ")")
    if round_no == 1:
        with open('alive.csv', mode='w', newline='') as csv_file:
            fieldnames = ['round', 'alive']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'round': round_no, 'alive': sheep_no})
    else:
        with open('alive.csv', mode='a', newline='') as csv_file:
            fieldnames = ['round', 'alive']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writerow({'round': round_no, 'alive': sheep_no})


def parse_config(file):
    config = ConfigParser()
    config.read(file)
    init = config.get('Terrain', 'InitPosLimit')
    sheep = config.get('Movement', 'SheepMoveDist')
    wolf = config.get('Movement', 'WolfMoveDist')
    if float(init) < 0 or float(sheep) < 0 or float(wolf) < 0:
        logging.error("Not positive number passed as argument")
        raise ValueError("Not positive number")
    # logging.debug("parse_config(", file, ") called, returned,", float(init), float(sheep), float(wolf))
    return float(init), float(sheep), float(wolf)


def simulation(sheep_no, round_no, init_pos_limit, sheep_move_dist, wolf_move_dist, wait, directory):
    # logging.debug("simulation(", sheep_no, round_no, init_pos_limit, sheep_move_dist, wolf_move_dist, wait,
    #               str(directory), ") called")
    sheep = setup(sheep_no, init_pos_limit)
    wolf = Wolf(0.0, 0.0)
    for i in range(1, round_no + 1):
        gen = ([x for x in sheep if x.status == "alive"])
        if not gen:
            print("All sheep are dead!")
            break
        for j in gen:
            if j.status == "alive":
                j.move(sheep_move_dist)
                j.dist = euclidean(j, wolf)
        nearest = min(gen, key=lambda shp: shp.dist)
        if nearest.dist <= wolf_move_dist:
            wolf.x = nearest.x
            wolf.y = nearest.y
            nearest.status = "dead"
        if nearest.dist > wolf_move_dist:
            wolf_move(wolf_move_dist, nearest, wolf)
        if nearest.status == "dead":
            x = nearest.no
        else:
            x = "none"
        print("Turn number:", i, "Wolf position: %.3f %.3f" % (wolf.x, wolf.y), "Number of living sheep:",
              gen.__len__(), "Dead sheep in this round: ", x)
        logging.info("Turn number: " + str(i) + " Wolf position: " + str(wolf.x) + ", " + str(wolf.y) +
                     " Number of living sheep:" + str(gen.__len__()) + " Dead sheep in this round: " + str(x))
        json_export(sheep, wolf, i, directory)
        csv_export(i, gen.__len__())
        if wait:
            input("Press a key to continue...")


def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s value must be positive" % value)
    logging.debug("check_positive(", value, ") called, returned,", ivalue)
    return ivalue


def main():
    sheep_no = 15
    round_no = 50
    wolf_move_dist = 1
    init_pos_limit = 10.0
    sheep_move_dist = 0.5
    wait = False
    directory = None

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help="set config file", action='store', dest='conf_file', metavar='FILE')
    parser.add_argument('-d', '--dir', action='store', help="choose where to save files", dest='directory',
                        metavar='DIR')
    parser.add_argument('-l', '--log', action='store', help="create log file with log LEVEL", dest='log_lvl',
                        metavar='LEVEL')
    parser.add_argument('-r', '--rounds', action='store',
                        help="choose for how many rounds should the simulation run", dest='round_no',
                        type=check_positive, metavar='NUM')
    parser.add_argument('-s', '--sheep', action='store',
                        help="choose how many sheep in the simulation", dest='sheep_no', type=check_positive,
                        metavar='NUM')
    parser.add_argument('-w', '--wait', action='store_true', help="wait for input after each round")
    args = parser.parse_args()
    if args.conf_file:
        sheep_move_dist, wolf_move_dist, init_pos_limit = parse_config(args.conf_file)
    if args.directory:
        directory = args.directory
    if args.log_lvl:
        if args.log_lvl == "DEBUG":
            lvl = logging.DEBUG
        elif args.log_lvl == "INFO":
            lvl = logging.INFO
        elif args.log_lvl == "WARNING":
            lvl = logging.WARNING
        elif args.log_lvl == "ERROR":
            lvl = logging.ERROR
        elif args.log_lvl == "CRITICAL":
            lvl = logging.CRITICAL
        else:
            raise ValueError("Invalid log level!")
        logging.basicConfig(level=lvl, filename="chase.log")
        logging.debug("debug")
    if args.round_no:
        round_no = args.round_no
    if args.sheep_no:
        sheep_no = args.sheep_no
    if args.wait:
        wait = args.wait
    simulation(sheep_no, round_no, init_pos_limit, sheep_move_dist, wolf_move_dist, wait, directory)


if __name__ == "__main__":
    main()
