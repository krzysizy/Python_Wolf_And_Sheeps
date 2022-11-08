import csv
import logging
import os
import random
import math
import json
import argparse
import configparser


class Sheep:
    def __init__(self, id_num, x, y, move_dist):
        self.x = x
        self.y = y
        self.move_dist = move_dist
        self.alive_or_dead = True
        self.id = id_num

    def move(self):
        dir_list = ['North', 'South', 'East', 'West']
        direction = random.choice(dir_list)
        if direction == 'North':
            self.y += self.move_dist
        elif direction == 'South':
            self.y -= self.move_dist
        elif direction == 'West':
            self.x -= self.move_dist
        elif direction == 'East':
            self.x += self.move_dist


class Wolf:
    def __init__(self, x, y, move_dist):
        self.x = x
        self.y = y
        self.move_dist = move_dist

    def move(self, nearest):
        if nearest is not None:
            dist_of_nearest_sheep = euclidean_dist(nearest.x, nearest.y, self.x, self.y)
            if dist_of_nearest_sheep > self.move_dist:
                x_an = self.move_dist * ((nearest.x - self.x) / dist_of_nearest_sheep)
                y_an = self.move_dist * ((nearest.y - self.y) / dist_of_nearest_sheep)
                self.x += x_an
                self.y += y_an
                return False
            else:
                self.x = nearest.x
                self.y = nearest.y
                nearest.alive_or_dead = False
                return True


def sheep_setup(sheep_num, init_pos_limit, sheep_move_dist):
    sheep = []
    for i in range(1, sheep_num + 1):
        sheep.append(Sheep(i, random.uniform(-init_pos_limit, init_pos_limit),
                           random.uniform(-init_pos_limit, init_pos_limit),
                           sheep_move_dist))
    return sheep


def euclidean_dist(x1, y1, x2, y2):
    euclidean_distance = math.sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2))
    logging.debug("euclidean_dist(" + str(x1) + ", " + str(y1) + str(x2) + ", " + str(y2)
                  + "), return: " + str(euclidean_distance))
    return euclidean_distance


def nearest_sheep(flock_of_sheep, wolf):
    j = 0
    while not flock_of_sheep[j].alive_or_dead:
        j += 1
    nearest = flock_of_sheep[j]
    nearest_dist = euclidean_dist(nearest.x, nearest.y, wolf.x, wolf.y)
    for i in range(j + 1, len(flock_of_sheep)):
        if flock_of_sheep[i].alive_or_dead:
            if euclidean_dist(flock_of_sheep[i].x, flock_of_sheep[i].y, wolf.x, wolf.y) <= nearest_dist:
                nearest = flock_of_sheep[i]
    logging.debug("nearest_sheep(" + str(flock_of_sheep) + ", " + str(wolf) + "), return: " + str(nearest))
    return nearest


def sheep_moves(sheep):
    for i in sheep:
        if i.alive_or_dead:
            i.move()
    logging.debug("sheep_moves(" + str(sheep) + "), return: ")


def alive_sheep(sheep):
    counter = 0
    for i in sheep:
        if i.alive_or_dead:
            counter += 1
    logging.debug("alive_sheep(" + str(sheep) + "), return: " + str(counter))
    return counter


def json_export(sheep, wolf, round_num, filename):
    dictionary = {
        "round_no": round_num,
        "wolf_pos": str(wolf.x) + ", " + str(wolf.y),
        "sheep_pos": []
    }
    for i in sheep:
        if i.alive_or_dead:
            dictionary["sheep_pos"].append(str(i.x) + ", " + str(i.y))
        else:
            dictionary["sheep_pos"].append('Null')
    if round_num == 1:
        f = open(filename, "w+")
    else:
        f = open(filename, "a")
    f.write(json.dumps(dictionary, indent=4))
    logging.debug("json_export(" + str(sheep) + ", " + str(wolf) + ", " + str(round_num) + ", " + filename
                  + "), return: ")
    f.close()


def csv_export(round_no, alive_sheep_no, filename):
    fieldnames = ['round_no', 'alive_sheep_no']
    if round_no == 1:
        csv_file = open(filename, "w+", newline='')
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
    else:
        csv_file = open(filename, "a", newline='')
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writerow({'round_no': round_no, 'alive_sheep_no': alive_sheep_no})
    logging.debug("csv_export(" + str(round_no) + ", " + str(alive_sheep_no) + ", " + filename + "), return: ")
    csv_file.close()


def simulation(rounds, sheep_num, init_pos_limit, sheep_move_dist, wolf_move_dist, wait, directory):
    sheep = sheep_setup(sheep_num, init_pos_limit, sheep_move_dist)
    wolf = Wolf(0.0, 0.0, wolf_move_dist)
    round_num = 1
    while round_num <= rounds and alive_sheep(sheep) != 0:
        sheep_moves(sheep)
        nearest = nearest_sheep(sheep, wolf)
        is_sheep_caught = wolf.move(nearest)
        json_export(sheep, wolf, round_num, create_file_path(directory, 'pos.json'))
        csv_export(round_num, alive_sheep(sheep), create_file_path(directory, 'alive.csv'))
        print("Round:", round_num,
              "\nWolf position:", round(wolf.x, 3), ",", round(wolf.y, 3),
              "\nAlive sheep number:", alive_sheep(sheep))
        if is_sheep_caught:
            additional_info = str("Sheep: " + str(nearest.id) + " was eaten by wolf")
            print("Sheep:", nearest.id, "was eaten by wolf")
        else:
            additional_info = str("Sheep: " + str(nearest.id) + " was chases by wolf")
            print("Sheep:", nearest.id, "was chases by wolf")
        logging.info("Round: " + str(round_num) +
                     ", Wolf position: " + str(round(wolf.x, 3)) + ", " + str(round(wolf.y, 3)) +
                     ", Alive sheep number: " + str(alive_sheep(sheep)) + ", " + additional_info)
        if wait:
            input("Press a key to continue...")
        round_num += 1


def get_config_info(file):
    config = configparser.ConfigParser()
    config.read(file)
    initPosLimit = float(config.get('Terrain', 'InitPosLimit'))
    wolf_move_dist = float(config.get('Movement', 'WolfMoveDist'))
    sheep_move_dist = float(config.get('Movement', 'SheepMoveDist'))
    if initPosLimit < 0 or wolf_move_dist < 0 or sheep_move_dist < 0:
        logging.error("Not positive number passed as argument")
        raise ValueError('Negative value!')
    logging.debug("get_config_info( " + str(file) + " ) called, returned: " + str(initPosLimit) + ", " + str(wolf_move_dist) + ", " + str(sheep_move_dist))
    return initPosLimit, wolf_move_dist, sheep_move_dist


def is_greater_than_zero(value):
    if value.isdigit():
        value = int(value)
    else:
        raise argparse.ArgumentTypeError("Cannot convert value %s to positive int!" % value)
    return value


def check_path(directory):
    path = os.path.join(os.getcwd(), directory)
    if not os.path.exists(path):
           os.mkdir(path)
    return path


def create_file_path(path, filename):
    return os.path.join(path, filename)


def main():
    rounds = 50
    sheep_num = 15
    wolf_move_dist = 1
    init_pos_limit = 10.0
    sheep_move_dist = 0.5
    wait = False
    directory = os.getcwd()
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help="set config file", action='store', dest='config_file', metavar='FILE')
    parser.add_argument('-d', '--dir', help="set directory to save files", action='store',
                        type=check_path, dest='directory', metavar='DIR')
    parser.add_argument('-l', '--log', action='store', help="choose level of event logs",
                        dest='log_lvl', metavar='LEVEL')
    parser.add_argument('-r', '--rounds', help="choose for how many rounds simulation should goes", nargs='?',
                        type=is_greater_than_zero, dest='rounds', default=50, metavar='NUM')
    parser.add_argument('-s', '--sheep', help="choose how many sheep take part in simulation", nargs='?',
                        type=is_greater_than_zero, dest='sheep_num', default=15, metavar='NUM')
    parser.add_argument('-w', '--wait', help="choose do you want stop simulation each round",
                        action='store_true')
    args = parser.parse_args()
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
        logging.basicConfig(level=lvl, filename="chase.log", filemode='w')
        logging.debug("logging config")
    if args.config_file:
        init_pos_limit, wolf_move_dist, sheep_move_dist = get_config_info(args.config_file)
    if args.directory:
        directory = args.directory
    if args.rounds:
        rounds = args.rounds
    if args.sheep_num:
        sheep_num = args.sheep_num
    if args.wait:
        wait = args.wait
    simulation(rounds, sheep_num, init_pos_limit, sheep_move_dist, wolf_move_dist, wait, directory)


if __name__ == "__main__":
    main()
