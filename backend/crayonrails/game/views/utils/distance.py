def manhattan_distance(location1, location2):
    [[x1, y1], [x2, y2]] = location1, location2
    return max(abs(x1 - x2), abs(y1 - y2))


def distances(location, other_locations):
    for other in other_locations:
        yield manhattan_distance(location, other)