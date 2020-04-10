import json
import random
from random import randint
import pathlib

from .models import GameAction

MAP_WIDTH = 87
MAP_HEIGHT = 50


def random_map_point(border=0):
    return [
        randint(border, MAP_WIDTH - border),
        randint(border, MAP_HEIGHT - border)
    ]


def manhattan_distance(location1, location2):
    [[x1, y1], [x2, y2]] = location1, location2
    return max(abs(x1 - x2), abs(y1 - y2))


def distances(location, other_locations):
    for other in other_locations:
        yield manhattan_distance(location, other)


def random_separate_map_points(target_number, border=0, distance_between=1):
    locations = []
    for i in range(target_number):
        location = random_map_point(border=border)
        if not locations or min(distances(location, locations)) > distance_between:
            locations.append(location)
    return locations


def random_city_name():
    with open(pathlib.Path(__file__).with_name("city-names.txt")) as names:
        return random.choice(names.readlines()).strip()


def random_goods(min_goods, max_goods):
    number = random.randint(min_goods, max_goods)
    with open(pathlib.Path(__file__).with_name("available-goods.txt")) as goods:
        for good in random.sample(goods.readlines(), number):
            yield good.strip()


def only_distant_locations(filtered_class, test_class, distance=2):
    for filterable in filtered_class:
        if min(distances(filterable, test_class)) > distance:
            yield filterable


def build_new_map(game):
    goods_list = list(random_goods(30, 35))

    major = random_separate_map_points(6, border=5, distance_between=8)
    medium = list(only_distant_locations(random_separate_map_points(30, border=3, distance_between=7), major))
    small = list(only_distant_locations(random_separate_map_points(45, border=3, distance_between=7), major + medium))

    cities = []
    for location in major:
        cities.append(("add_major_city", location, random.sample(goods_list, random.randint(0, 1))))
    for location in medium:
        cities.append(("add_medium_city", location, random.sample(goods_list, random.choice([0,0,1,1,1,1,2,2,2]))))
    for location in small:
        cities.append(("add_small_city", location, random.sample(goods_list, random.choice([0,0,1,1,1,1,2,2,2]))))

    for index, (action, location, goods) in enumerate(cities):
        if "city" in action:
            GameAction(game_id=game.id, sequence_number=index, type=action, data=json.dumps({
                "name": random_city_name(),
                "location": location,
                "available_goods": goods
            })).save()
