import json
import random
from random import randint
import secrets
import pathlib

from .models import GameAction, PlayerSlot

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
    goods_list = list(random_goods(30, 35))

    major = random_separate_map_points(6, border=5, distance_between=8)
    medium = list(only_distant_locations(random_separate_map_points(30, border=3, distance_between=7), major))
    small = list(only_distant_locations(random_separate_map_points(45, border=3, distance_between=5), major + medium))

    cities = []
    for location in major:
        cities.append(("add_major_city", location, random.sample(goods_list, random.choice([0, 0, 1]))))
    for location in medium:
        cities.append(
            ("add_medium_city", location, random.sample(goods_list, random.choice([0, 0, 1, 1, 1, 1, 2, 2, 2]))))
    for location in small:
        cities.append(
            ("add_small_city", location, random.sample(goods_list, random.choice([0, 0, 1, 1, 1, 1, 2, 2, 2]))))

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

    # generate rivers
    # river_seeds = list(set(tuple(random_map_point(border=-1)) for i in range(50)))
    #
    # rivers = []
    #
    # for points in (random.sample(river_seeds, 3) for i in range(3)):
    #     points.sort(key=lambda point: (point[1], point[0]))
    #     keypoints = []
    #     for i1, point in enumerate(points[:-1]):
    #         point2 = points[i1 + 1]
    #         keypoints.extend(list(directed_random_walk(point, point2))[:-1])
    #     rivers.append(keypoints)
    #
    # for river in rivers:
    #     game_action = GameAction(
    #         game_id=game.id,
    #         sequence_number=sequence_number,
    #         type="add_river",
    #         data=json.dumps({
    #             "locations": river
    #         }))
    #     game_action.save()
    #     sequence_number += 1


def random_joincode():
    return secrets.token_hex(32)


def random_color():
    return f"rgb({random.randint(30, 255)},{random.randint(30, 255)},{random.randint(30, 255)})"


def build_player_slots(game, creator):
    PlayerSlot(game_id=game.id, user_id=creator.id, color="#ff2234", role="creator", index=1).save()
    [PlayerSlot(game_id=game.id, color=random_color(), joincode=random_joincode(), role="guest", index=i+1).save() for i in range(5)]
