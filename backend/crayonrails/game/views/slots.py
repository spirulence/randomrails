import base64

from django.http import HttpResponseForbidden, JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST

from ..models import PlayerSlot
from .utils.permissions import is_player, is_creator


def slots_view_all(request, game_id):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    slots = []
    for s in PlayerSlot.objects.filter(game_id=game_id):
        slots.append({"playerNumber": s.index, "name": s.screenname, "color": s.color})

    return JsonResponse({
        "result": slots
    })


def slots_view_joincodes(request, game_id):
    if not is_creator(request, game_id):
        return HttpResponseForbidden()

    slots = []
    for s in PlayerSlot.objects.filter(game_id=game_id):
        slots.append({"playerNumber": s.index, "name": s.screenname, "color": s.color, "joincode": s.joincode})

    return JsonResponse({
        "result": slots
    })


def slot_view_mine(request, game_id):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    slot = PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)

    return JsonResponse({
        "result": {
            "playerNumber": slot.index,
            "name": slot.screenname,
            "color": slot.color
        }
    })


@require_POST
def slot_set_color(request, game_id, player_number, color):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    color_decoded = str(base64.b64decode(bytes(color, encoding="utf8")), encoding="utf8").lower()

    options = [
        "#00ffcc", "#0b8a00", "#ffbf00", "#00bfff", "#0000ff", "#bf00ff", "#9900cc", "#cc0099", "#660066",
    ]

    if not color_decoded.startswith("#") or not len(color_decoded) == 7 or any(
            map(lambda c: c not in "0123456789abcdef", color_decoded[1:])) or color_decoded not in options:
        return HttpResponseBadRequest()

    slot = PlayerSlot.objects.get(game_id=game_id, index=player_number)
    conflict_slots = PlayerSlot.objects.filter(game_id=game_id, color=color_decoded)[:1]

    if is_creator(request, game_id) or slot.user_id == request.user.id and not conflict_slots:
        slot.color = color_decoded
        slot.save()
        return JsonResponse({
            "result": "success"
        })
    else:
        return HttpResponseBadRequest("can't alter that user's color or it is already in use")