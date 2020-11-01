import json
import pathlib
import random

from .standard import random_goods, random_separate_map_points, only_distant_locations, random_city_names, \
    random_map_point, only_close_locations
from ...models import GameAction
from .country_grid import CountryMap

MAP_WIDTH = 87
MAP_HEIGHT = 50


def random_country_names(n):
    with open(pathlib.Path(__file__).with_name("country-names.txt")) as names:
        return [name.strip() for name in random.sample(list(names.readlines()), n)]


def build_new_map(game):
    sequence_number = 0

    # generate all cities
    goods_list = list(random_goods(25, 30))

    major = random_separate_map_points(6, border=5, distance_between=8)
    medium = list(only_distant_locations(random_separate_map_points(30, border=3, distance_between=7), major))
    small = list(only_distant_locations(random_separate_map_points(45, border=3, distance_between=5), major + medium))

    cities = []
    for location in major:
        cities.append(("add_major_city", location, random.sample(goods_list, random.choice([0, 0, 1]))))
    for location in medium:
        cities.append(
            ("add_medium_city", location,
             random.sample(goods_list, random.choice([0, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 3, 3]))))
    for location in small:
        cities.append(
            ("add_small_city", location,
             random.sample(goods_list, random.choice([0, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 3, 3]))))

    city_names = random_city_names(len(cities))

    for index, (action, location, goods) in enumerate(cities):
        GameAction(game_id=game.id, sequence_number=sequence_number, type=action, data=json.dumps({
            "name": city_names[index],
            "location": location,
            "available_goods": goods
        })).save()
        sequence_number += 1

    # generate mountains
    mountain_seeds = set(tuple(random_map_point()) for i in range(50))
    possible_clump_locations = set(tuple(random_map_point()) for i in range(2000))
    mountain_clumps = list(only_close_locations(possible_clump_locations, mountain_seeds, distance=3))

    mountains = list(mountain_seeds) + mountain_clumps
    mountains_not_on_cities = only_distant_locations(
        only_distant_locations(mountains, major),
        medium + small, distance=1)

    for x, y in mountains_not_on_cities:
        game_action = GameAction(
            game_id=game.id,
            sequence_number=sequence_number,
            type="add_mountain",
            data=json.dumps({
                "location": [x, y]
            }))
        game_action.save()
        sequence_number += 1

    grid = CountryMap()
    grid.generate(MAP_WIDTH, MAP_HEIGHT)

    country_colors = "#ed1c24ff #f58e90ff #fdfffcff #235789ff #8a9546ff #f1d302ff #7a6a01ff #020100ff".split()
    country_names = random_country_names(8)

    for country_number, cells in grid.cells_by_country.items():

        min_x = min(cells, key=lambda cell: cell[0])[0]
        max_x = max(cells, key=lambda cell: cell[0])[0]
        min_y = min(cells, key=lambda cell: cell[1])[1]
        max_y = max(cells, key=lambda cell: cell[1])[1]

        label_x, label_y = (min_x + max_x) // 2, (min_y + max_y) // 2

        if (label_x, label_y) not in cells:
            label_x, label_y = random.choice(cells)

        GameAction(
            game_id=game.id,
            sequence_number=sequence_number,
            type="add_country",
            data=json.dumps({
                "name": country_names[country_number],
                "color": country_colors[country_number],
                "cells": cells,
                "labelPoint": (label_x, label_y)
            })).save()
        sequence_number += 1
