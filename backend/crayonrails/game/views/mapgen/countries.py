import json
import pathlib
import random
from collections import namedtuple

import numpy
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, LineString, MultiPolygon, MultiPoint, Point
import shapely.ops

from ..maprender import grid_to_board_x, grid_to_board_y, rows, columns
from ..utils import gameactions
from ..utils.distance import distances
from ...models import GameAction

MAP_WIDTH = 87
MAP_HEIGHT = 50


def random_map_point(border=0):
    return [
        random.randint(border, MAP_WIDTH - border),
        random.randint(border, MAP_HEIGHT - border)
    ]


def random_separate_map_points(target_number, border=0, distance_between=1, not_in=set()):
    locations = []
    for i in range(target_number):
        location = random_map_point(border=border)
        if not locations or min(distances(location, locations)) > distance_between:
            if tuple(location) not in not_in:
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


Country = namedtuple("Country", "name border point_within all_grid_points_within")


def country_names():
    with open(pathlib.Path(__file__).with_name("country-names.txt")) as country_names_file:
        return [n.strip() for n in country_names_file.readlines()]


def points_in(w):
    for row in range(rows):
        for column in range(columns):
            x = grid_to_board_x(column, row)
            y = grid_to_board_y(column, row)
            if w.buffer(5).contains(Point(x, y)):
                yield column, row


def generate_water(game_id):
    points = []
    for i in range(150):
        points.append((random.randrange(0, 3500), random.randrange(0, 2000)))

    regions = shapely.ops.voronoi_diagram(MultiPoint(points), tolerance=0.5)

    water = shapely.ops.cascaded_union(random.sample(list(regions), 40)).buffer(200).buffer(-400).intersection(Polygon([(0, 0), (3500, 0), (3500, 2000), (0, 2000), (0, 0)]))

    water = list(w for w in water if w.area > 400)

    for w in water:
        contains = list(points_in(w))
        if contains:
            yield w, contains


def generate_countries(game_id):
    points = []
    for city, (x, y) in gameactions.get_cities_map(game_id).items():
        points.append([grid_to_board_x(x, y), grid_to_board_y(x, y)])

    points = MultiPoint(points)

    diagram = shapely.ops.voronoi_diagram(points, envelope=Polygon([(0, 0), (3500, 0), (3500, 2000), (0, 2500)]))

    # points.append([-500, -500])
    # points.append([4000, -500])
    # points.append([4000, 2500])
    # points.append([-500, 2500])
    #
    # vor = Voronoi(numpy.array(points))
    #
    # polygons = []
    #
    # for index, region in enumerate(vor.regions):
    #     if not -1 in region:
    #         polygons.append(Polygon([(int(vor.vertices[i][0]), int(vor.vertices[i][1])) for i in region]))
    #
    # for join_attempt in range(300):
    #     i1, i2 = random.sample(range(len(polygons)), 2)
    #     if polygons[i1].distance(polygons[i2]) < 0.5:
    #         print("joining", i1, i2)
    #         polygons.append(cascaded_union([polygons[i1], polygons[i2]]))
    #         polygons.remove(polygons[i1])
    #         polygons.remove(polygons[i2])
    #
    # cropped_polygons = []
    # cropper = Polygon([(-5, -5), (3505, -5), (3505, 2005), (-5, 2005), (-5, -5)])
    # for p in polygons:
    #     cropped = p.intersection(cropper)
    #     if isinstance(cropped, MultiPolygon):
    #         for p1 in list(cropped):
    #             cropped_polygons.append(p1)
    #     else:
    #         cropped_polygons.append(cropped)
    #
    # polygons = [p.buffer(100).buffer(-100) for p in cropped_polygons]
    #
    # names = random.sample(country_names(), len(polygons))
    #
    # for name, p in zip(names, polygons):
    #     centroid_x, centroid_y = p.centroid.x, p.centroid.y
    #     centroid_x = min(max(centroid_x, 200), 3300)
    #     centroid_y = min(max(centroid_y, 200), 1800)
    #     yield Country(
    #         name=name,
    #         border=list(p.exterior.coords),
    #         point_within=[centroid_x, centroid_y],
    #         all_grid_points_within=[])


def build_new_map(game):
    sequence_number = 0

    in_water = set()
    for water, contains in generate_water(game.id):
        game_action = GameAction(
            game_id=game.id,
            sequence_number=sequence_number,
            type="add_water",
            data=json.dumps({
                "coords": list(water.exterior.coords),
                "contains": contains
            }))
        game_action.save()
        in_water.update(contains)
        sequence_number += 1

    # generate all cities
    goods_list = list(random_goods(25, 30))

    major = random_separate_map_points(6, border=5, distance_between=8, not_in=in_water)
    medium = list(only_distant_locations(random_separate_map_points(30, border=3, distance_between=7, not_in=in_water), major))
    small = list(only_distant_locations(random_separate_map_points(45, border=3, distance_between=5, not_in=in_water), major + medium))

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

    # for country in generate_countries(game.id):
    #     game_action = GameAction(
    #         game_id=game.id,
    #         sequence_number=sequence_number,
    #         type="add_country",
    #         data=json.dumps({
    #             "name": country.name,
    #             "coords": country.border,
    #             "labelPoint": country.point_within
    #         }))
    #     game_action.save()
    #     sequence_number += 1
