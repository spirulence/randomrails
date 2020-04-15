import json

from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST

from ..utils.permissions import is_player
from ...models import PlayerSlot, GameAction


@require_POST
def action_move_train(request, game_id, x, y):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    slot = PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)

    next_sequence_number = GameAction.objects.filter(game_id=game_id).order_by('-sequence_number').first().sequence_number + 1
    game_action = GameAction(
        game_id=game_id,
        sequence_number=next_sequence_number,
        type="move_train",
        data=json.dumps({
            "playerId": slot.id,
            "to": [x, y]
        }))
    game_action.save()
    return JsonResponse({
        "result": "success"
    })