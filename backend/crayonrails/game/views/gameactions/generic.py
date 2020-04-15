import json

from django.http import HttpResponseForbidden, JsonResponse

from ..utils.gameactions import last_game_action
from ..utils.permissions import is_player
from ...models import GameAction


def actions(request, game_id):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    query = GameAction.objects.filter(game_id=game_id).order_by('sequence_number')
    actions_result = [{"sequenceNumber": a.sequence_number, "type": a.type, "data": json.loads(a.data)} for a in query]

    return JsonResponse({
        "result": actions_result
    })


def actions_after(request, game_id, sequence_number):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    query = GameAction.objects.filter(game_id=game_id, sequence_number__gt=sequence_number).order_by('sequence_number')
    actions_result = [{"sequenceNumber": a.sequence_number, "type": a.type, "data": json.loads(a.data)} for a in query]

    return JsonResponse({
        "result": actions_result
    })