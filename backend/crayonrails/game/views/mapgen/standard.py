import json
import pathlib
import random

from ..utils.distance import distances
from ...models import GameAction

MAP_WIDTH = 87
MAP_HEIGHT = 50


def random_map_point(border=0):
    return [
        random.randint(border, MAP_WIDTH - border),
        random.randint(border, MAP_HEIGHT - border)
    ]


def random_separate_map_points(target_number, border=0, distance_between=1):
    locations = []
    for i in range(target_number):
        location = random_map_point(border=border)
        if not locations or min(distances(location, locations)) > distance_between:
            locations.append(location)
    return locations


def random_city_names(n):
    with open(pathlib.Path(__file__).with_name("city-names.txt")) as names:
        return [name.strip() for name in random.sample(list(names.readlines()), n)]


def random_goods(min_goods, max_goods):
    number = random.randint(min_goods, max_goods)
    with open(pathlib.Path(__file__).with_name("available-goods.txt")) as goods:
        for good in random.sample(goods.readlines(), number):
            yield good.strip()


def only_distant_locations(filtered_class, test_class, distance=2):
    for filterable in filtered_class:
        if min(distances(filterable, test_class)) > distance:
            yield filterable


def only_close_locations(filtered_class, test_class, distance=5):
    for filterable in filtered_class:
        if min(distances(filterable, test_class)) < distance:
            yield filterable


def directed_random_walk(point, point2):
    [x1, y1], [x2, y2] = point, point2
    x_diff, y_diff = x2 - x1, y2 - y1

    if x_diff > 0:
        x_progress = 1
    else:
        x_progress = -1

    if y_diff > 0:
        y_progress = 1
    else:
        y_progress = -1

    paces = [(x_progress, y_progress)] * min(x_diff, y_diff)
    if x_diff > y_diff:
        paces += [(x_progress, 0)] * (x_diff - y_diff)
    elif y_diff > x_diff:
        paces += [(0, y_progress)] * (y_diff - x_diff)

    random.shuffle(paces)

    current = point
    yield current

    for pace in paces:
        current = current[0] + pace[0], current[1] + pace[1]
        yield current


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
            ("add_medium_city", location, random.sample(goods_list, random.choice([0, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 3, 3]))))
    for location in small:
        cities.append(
            ("add_small_city", location, random.sample(goods_list, random.choice([0, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 3, 3]))))

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