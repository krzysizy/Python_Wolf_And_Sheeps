import csv
import os
import random
import math
import json
import argparse


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
    return nearest


def sheep_moves(sheep):
    for i in sheep:
        if i.alive_or_dead:
            i.move()


def alive_sheep(sheep):
    counter = 0
    for i in sheep:
        if i.alive_or_dead:
            counter += 1
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
    csv_file.close()


def simulation(rounds, sheep_num, init_pos_limit, sheep_move_dist, wolf_move_dist, wait):
    sheep = sheep_setup(sheep_num, init_pos_limit, sheep_move_dist)
    wolf = Wolf(0.0, 0.0, wolf_move_dist)
    round_num = 1
    while round_num <= rounds and alive_sheep(sheep) != 0:
        sheep_moves(sheep)
        nearest = nearest_sheep(sheep, wolf)
        is_sheep_caught = wolf.move(nearest)
        json_export(sheep, wolf, round_num, 'pos.json')
        csv_export(round_num, alive_sheep(sheep), 'alive.csv ')
        print("Round:", round_num,
              "\nWolf position:", round(wolf.x, 3), ",", round(wolf.y, 3),
              "\nAlive sheep number:", alive_sheep(sheep))
        if is_sheep_caught:
            print("Sheep:", nearest.id,  "was eaten by wolf")
        else:
            print("Sheep:", nearest.id, "was chases by wolf")
        if wait:
            input("Press a key to continue...")
        round_num += 1


def main():
    rounds = 50
    sheep_num = 15
    wolf_move_dist = 1
    init_pos_limit = 10.0
    sheep_move_dist = 0.5
    wait = False
    directory = None
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help="set config file", action='store', dest='config_file', metavar='FILE')
    parser.add_argument('-d', '--dir', help="set directory to save files", action='store',
                        dest='directory', default=os.getcwd(), metavar='DIR')
    parser.add_argument('-l', '--log', action='store', help="choose level of event logs",
                        dest='log_lvl', metavar='LEVEL')
    parser.add_argument('-r', '--rounds', help="choose for how many rounds simulation goes", type=int, dest='rounds',
                        default=50, metavar='NUM')
    parser.add_argument('-s', '--sheep', help="choose how many sheep take part in simulation", type=int,
                        dest='sheep_num', default=15, metavar='NUM')
    parser.add_argument('-w', '--wait', help="choose do you want stop simulation each round",
                        action='store_true')
    args = parser.parse_args()
    simulation(rounds, sheep_num, init_pos_limit, sheep_move_dist, wolf_move_dist, wait)


if __name__ == "__main__":
    main()