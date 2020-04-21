import json
import tempfile

import numpy
from django.http import HttpResponseForbidden, HttpResponse
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg
from scipy.spatial import Voronoi

from .utils import gameactions
from .utils.permissions import is_player
from ..models import GameAction

columns = 87
rows = 50

spaceBetween = 40
circleRadius = 3
mountainSize = spaceBetween / 4

def grid_to_board_x(x, y):
    if y % 2 == 0:
        return x * spaceBetween + spaceBetween / 2
    else:
        return x * spaceBetween + spaceBetween


def grid_to_board_y(x, y):
    return y * spaceBetween + spaceBetween / 2


def render_to_svg(water_actions, mountain_actions, country_actions):
    mountains = set(tuple(json.loads(a.data)["location"]) for a in mountain_actions)

    with tempfile.NamedTemporaryFile(suffix=".svg") as svg_file:
        svg_file.write(b"<svg viewBox='0 0 3500 2000'>")

        water_points = set()
        for water in water_actions:
            coords = json.loads(water.data)["coords"]
            water_points.update(tuple(c) for c in json.loads(water.data)["contains"])
            coord_strings = []
            for x, y in coords:
                coord_strings.append(f'{x} {y}')

            water_color = '#42e9f5'

            if coord_strings:
                path = f'<path fill="{water_color}" stroke="black" strokeWidth="5px" d="M {coord_strings[0]} {" L ".join(coord_strings[1:])}"/>'.encode()
                svg_file.write(path)

        for row in range(rows):
            for column in range(columns):
                x = grid_to_board_x(column, row)
                y = grid_to_board_y(column, row)

                if (column, row) not in water_points:
                    if (column, row) in mountains:
                        svg_file.write(f'<path fill="black" d="M {x} {y - mountainSize} L {x + mountainSize} {y + mountainSize} L {x - mountainSize} {y + mountainSize}"/>'.encode())
                    else:
                        svg_file.write(f"<circle cx='{x}' cy='{y}' r='{circleRadius}' fill='black'/>".encode())

        for country in country_actions:
            coords = json.loads(country.data)["coords"]
            coord_strings = []
            for x, y in coords:
                coord_strings.append(f'{x} {y}')

            if coord_strings:
                path = f'<path fill="none" stroke-width="5px" stroke="black" d="M {coord_strings[0]} {" L ".join(coord_strings[1:])}"/>'.encode()
                svg_file.write(path)

        svg_file.write(b"</svg>")

        svg_file.seek(0)

        drawing = svg2rlg(svg_file.name)
        return renderPM.drawToString(drawing, fmt="jpg")


def map_render(request, game_id):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    water = GameAction.objects.filter(game_id=game_id, type="add_water")
    mountains = GameAction.objects.filter(game_id=game_id, type="add_mountain")
    countries = GameAction.objects.filter(game_id=game_id, type="add_country")

    as_string = render_to_svg(water, mountains, countries)

    return HttpResponse(as_string, content_type="image/jpg")


# def render_cells(game_id):
#     points = []
#     for city, (x, y) in gameactions.get_cities_map(game_id).items():
#         points.append([grid_to_board_x(x, y), grid_to_board_y(x, y)])
#
#     points.append([-500, -500])
#     points.append([4000, -500])
#     points.append([4000, 2500])
#     points.append([-500, 2500])
#
#     vor = Voronoi(numpy.array(points))
#
#     with tempfile.NamedTemporaryFile(suffix=".svg") as svg_file:
#         svg_file.write(b"<svg viewBox='0 0 3500 2000'>")
#
#         for region in vor.regions:
#             strings = []
#
#             for index in region:
#                 if index != -1:
#                     x, y = vor.vertices[index]
#                     strings.append(f'{x} {y}')
#
#             if strings:
#                 path = f'<path fill="none" stroke="black" d="M {strings[0]} {" L ".join(strings[1:])}"/>'.encode()
#                 svg_file.write(path)
#
#         svg_file.write(b"</svg>")
#
#         svg_file.seek(0)
#
#         drawing = svg2rlg(svg_file.name)
#         return renderPM.drawToString(drawing, fmt="jpg")
#
#
# def voronoi_render(request, game_id):
#     if not is_player(request, game_id):
#         return HttpResponseForbidden()
#
#     cells = render_cells(game_id)
#
#     return HttpResponse(cells, content_type="image/jpg")


