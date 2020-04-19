import json

import networkx

from .gameactions import get_current_track
from ..utils.adjacency import are_adjacent
from ...models import GameAction


def filter_paths_by_length(paths, max_length):
    for destination, path in paths.items():
        if 2 <= len(path) <= max_length + 1:
            yield destination, path[1:]


def get_major_city_track(game_id):
    track = set()

    for city_action in GameAction.objects.filter(game_id=game_id, type="add_major_city"):
        center_x, center_y = json.loads(city_action.data)["location"]

        deltas = [
            (-1, -1), (0, -1), (1, -1),
                (-1, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1),
        ]

        for dx, dy in deltas:
            if are_adjacent((center_x, center_y), (center_x + dx, center_y + dy)):
                track.add((center_x, center_y, center_x + dx, center_y + dy))
                for dx2, dy2 in deltas:
                    if are_adjacent((center_x, center_y), (center_x + dx2, center_y + dy2)):
                        if are_adjacent((center_x + dx, center_y + dy), (center_x + dx2, center_y + dy2)):
                            track.add((center_x + dx, center_y + dy, center_x + dx2, center_y + dy2))

    return track


def compute_paths_from(game_id, location, max_length=12):
    G = networkx.Graph()

    for x1, y1, x2, y2 in get_current_track(game_id):
        G.add_edge((x1, y1), (x2, y2))
        
    for x1, y1, x2, y2 in get_major_city_track(game_id):
        G.add_edge((x1, y1), (x2, y2))

    x, y = location

    paths = networkx.shortest_path(G, source=(x, y))

    return list(filter_paths_by_length(paths, max_length))