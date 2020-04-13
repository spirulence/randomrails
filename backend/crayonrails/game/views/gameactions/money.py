import json

from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_POST

from . import actiontypes
from ..utils.permissions import is_creator, is_player
from ...models import GameAction, PlayerSlot


@require_POST
def action_adjust_money(request, game_id, player, amount):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    request_user_slot = PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)
    slot_to_adjust = PlayerSlot.objects.get(game_id=game_id, index=player)

    if slot_to_adjust.id != request_user_slot.id and not is_creator(request, game_id):
        return HttpResponseForbidden()

    if amount == 0:
        return HttpResponseBadRequest("must add non-zero amount of money")

    next_sequence_number = GameAction.objects.filter(game_id=game_id).order_by('-sequence_number').first().sequence_number + 1

    actiontypes.money_adjust(
        game_id, next_sequence_number, slot_to_adjust.index, amount
    ).save()
    return JsonResponse({
        "result": "success"
    })
