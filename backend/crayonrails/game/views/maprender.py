import json
import tempfile

from django.http import HttpResponseForbidden, HttpResponse
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg

from .utils.permissions import is_player
from ..models import GameAction

spaceBetween = 40
circleRadius = 3
columns = 87
rows = 50
mountainSize = spaceBetween / 4

# function
# gridToBoardPixelX(x, y)
# {
# if (y % 2 === 0)
# {
# return x * spaceBetween + spaceBetween / 2
# } else {
# return x * spaceBetween + spaceBetween
# }
# }
#
# function
# gridToBoardPixelY(x, y)
# {
# return y * spaceBetween + spaceBetween / 2
# }


def grid_to_board_x(x, y):
    if y % 2 == 0:
        return x * spaceBetween + spaceBetween / 2
    else:
        return x * spaceBetween + spaceBetween


def grid_to_board_y(x, y):
    return y * spaceBetween + spaceBetween / 2


def render_to_svg(actions):
    mountains = set(tuple(json.loads(a.data)["location"]) for a in actions)

    with tempfile.NamedTemporaryFile(suffix=".svg") as svg_file:
        svg_file.write(b"<svg viewBox='0 0 3500 2000'>")

        for row in range(rows):
            for column in range(columns):
                x = grid_to_board_x(column, row)
                y = grid_to_board_y(column, row)

                if (column, row) in mountains:
                    svg_file.write(f'<path fill="black" d="M {x} {y - mountainSize} L {x + mountainSize} {y + mountainSize} L {x - mountainSize} {y + mountainSize}"/>'.encode())
                else:
                    svg_file.write(f"<circle cx='{x}' cy='{y}' r='{circleRadius}' fill='black'/>".encode())

        svg_file.write(b"</svg>")

        svg_file.seek(0)

        drawing = svg2rlg(svg_file.name)
        return renderPM.drawToString(drawing, fmt="jpg")


def map_render(request, game_id):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    actions = GameAction.objects.filter(game_id=game_id, type="add_mountain")

    as_string = render_to_svg(actions)

    return HttpResponse(as_string, content_type="image/jpg")


