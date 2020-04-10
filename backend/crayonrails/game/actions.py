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


def random_goods(min, max):
    number = random.randint(min, max)
    with open(pathlib.Path(__file__).with_name("available-goods.txt")) as goods:
        for good in random.sample(goods.readlines(), number):
            yield good.strip()


def random_cities(count, size):
    if size == "major":
        for i in random_separate_map_points(count, border=5, distance_between=8):
            yield "add_major_city", i, list(random_goods(0, 1))
    elif size == "medium":
        for i in random_separate_map_points(count, border=3, distance_between=7):
            yield "add_medium_city", i, list(random_goods(0, 2))
    elif size == "small":
        for i in random_separate_map_points(count, border=3, distance_between=7):
            yield "add_small_city", i, list(random_goods(0, 1))


def build_new_map(game):
    cities = list(random_cities(6, "major")) + list(random_cities(20, "medium")) + list(random_cities(35, "small"))

    for index, (action, location, goods) in enumerate(cities):
        if "city" in action:
            GameAction(game_id=game.id, sequence_number=index, type=action, data=json.dumps({
                "name": random_city_name(),
                "location": location,
                "available_goods": goods
            })).save()
