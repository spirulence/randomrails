import random
from collections import defaultdict


class CountryMap(object):
    NOT_ASSIGNED = -1
    ADJACENCY_VECTORS = [(x, y) for x in [-1, 0, 1] for y in [-1, 0, 1] if (x, y) != (0, 0)]

    def __init__(self):
        self.all_coordinates = []
        self.cells = []
        self.num_countries = 0
        self.grid_width, self.grid_height = 0, 0
        self.cells_by_country = defaultdict(list)

    def generate(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height

        min_countries = 4
        max_countries = 8

        self.num_countries = random.randint(min_countries, max_countries)

        self.generate_grid(grid_height, grid_width)

        self.all_coordinates = [(x, y) for x in range(grid_width) for y in range(grid_height)]

        self.seed_countries()

        for i in range(len(self.all_coordinates) // 4):
            self.grow()

        for i in range(5):
            self.blur()

        self.cells_by_country = defaultdict(list)
        for x, y in self.all_coordinates:
            self.cells_by_country[self.cells[x][y]].append((x, y))

    def seed_countries(self):
        for country_number, (x, y) in enumerate(random.sample(self.all_coordinates, self.num_countries)):
            self.cells[x][y] = country_number

    def generate_grid(self, grid_height, grid_width):
        self.cells = []
        for i in range(grid_width):
            column = []
            for j in range(grid_height):
                column.append(self.NOT_ASSIGNED)
            self.cells.append(column)

    def only_unassigned(self, coordinates):
        for x, y in coordinates:
            if self.cells[x][y] == self.NOT_ASSIGNED:
                yield x, y

    def only_assigned(self, coordinates):
        for x, y in coordinates:
            if self.cells[x][y] != self.NOT_ASSIGNED:
                yield x, y

    def grow(self):
        random_order = random.sample(self.all_coordinates, len(self.all_coordinates) // 36)
        for x, y in self.only_unassigned(random_order):
            for check_x, check_y in self.only_assigned(self.random_check_coordinates(x, y)):
                self.cells[x][y] = self.cells[check_x][check_y]

    def blur(self):
        for x, y in self.all_coordinates:
            count = self.count_adjacent_cells_of_other_colors(x, y)
            if count >= 6:
                rand_x, rand_y = random.choice(list(self.adjacent_coordinates(x, y)))
                self.cells[x][y] = self.cells[rand_x][rand_y]

    def only_in_bounds(self, x, y, deltas):
        for delta_x, delta_y in deltas:
            check_x = delta_x + x
            check_y = delta_y + y
            x_in_bounds = 0 <= check_x < self.grid_width
            y_in_bounds = 0 <= check_y < self.grid_height
            if x_in_bounds and y_in_bounds:
                yield check_x, check_y

    def random_check_coordinates(self, x, y):
        for check_x, check_y in self.only_in_bounds(x, y, random.sample(self.ADJACENCY_VECTORS, 7)):
            yield check_x, check_y

    def adjacent_coordinates(self, x, y):
        for check_x, check_y in self.only_in_bounds(x, y, self.ADJACENCY_VECTORS):
            yield check_x, check_y

    def count_adjacent_cells_of_other_colors(self, x, y):
        count = sum(self.cells[ax][ay] != self.cells[x][y] for ax, ay in self.adjacent_coordinates(x, y))
        return count
