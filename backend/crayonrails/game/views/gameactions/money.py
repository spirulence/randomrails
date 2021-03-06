import json

from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_POST

from . import actiontypes
from ..utils.permissions import is_creator, is_player
from ...models import GameAction, PlayerSlot


@require_POST
def action_adjust_money(request, game_id, player_id, sign, amount):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    if sign not in ("plus", "minus"):
        return HttpResponseBadRequest("invalid sign supplied")

    if sign == "minus":
        amount = -amount

    if not is_creator(request, game_id):
        return HttpResponseForbidden()

    if amount == 0:
        return HttpResponseBadRequest("must add non-zero amount of money")

    next_sequence_number = GameAction.objects.filter(game_id=game_id).order_by('-sequence_number').first().sequence_number + 1

    actiontypes.money_adjust(
        game_id, next_sequence_number, player_id, amount
    ).save()
    return JsonResponse({
        "result": "success"
    })
