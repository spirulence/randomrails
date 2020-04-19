import json

from django.http import HttpResponseForbidden, JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST

from ..utils.gameactions import get_existing_track, get_remaining_train_movement
from ..utils.gameflow import is_players_turn
from ..utils.permissions import is_player
from ..utils.trackgraph import compute_paths_from
from ...models import PlayerSlot, GameAction


@require_POST
def action_move_train(request, game_id, x, y):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    if not is_players_turn(request, game_id):
        return HttpResponseBadRequest("it is not your turn")

    slot = PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)

    current_location = None
    for action in GameAction.objects.filter(game_id=game_id, type="move_train").order_by('sequence_number'):
        if json.loads(action.data)["playerId"] == slot.id:
            current_location = json.loads(action.data)["to"]

    if current_location:
        movement_left = get_remaining_train_movement(game_id)
        for (destination_x, destination_y), path in compute_paths_from(game_id=game_id, location=current_location, max_length=movement_left):
            if (destination_x, destination_y) == (x, y):
                next_sequence_number = GameAction.objects.filter(game_id=game_id).order_by(
                    '-sequence_number').first().sequence_number + 1
                game_action = GameAction(
                    game_id=game_id,
                    sequence_number=next_sequence_number,
                    type="move_train",
                    data=json.dumps({
                        "playerId": slot.id,
                        "movementUsed": len(path),
                        "path": path,
                        "to": [x, y]
                    }))
                game_action.save()
                return JsonResponse({
                    "result": "success"
                })

        return HttpResponseBadRequest("you're not connected to that location")
    else:
        connected_to = False

        for points, player in get_existing_track(game_id).items():
            [from_x, from_y], [to_x, to_y] = points
            if (x, y) == (from_x, from_y) or (x, y) == (to_x, to_y):
                if player == slot.id:
                    connected_to = True

        if not connected_to:
            return HttpResponseBadRequest("you're not connected to that location")

        next_sequence_number = GameAction.objects.filter(game_id=game_id).order_by('-sequence_number').first().sequence_number + 1
        game_action = GameAction(
            game_id=game_id,
            sequence_number=next_sequence_number,
            type="move_train",
            data=json.dumps({
                "playerId": slot.id,
                "movementUsed": 0,
                "path": [],
                "to": [x, y]
            }))
        game_action.save()
        return JsonResponse({
            "result": "success"
        })


def get_train_destinations(request, game_id):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    slot = PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)

    current_location = None
    for action in GameAction.objects.filter(game_id=game_id, type="move_train").order_by('sequence_number'):
        if json.loads(action.data)["playerId"] == slot.id:
            current_location = json.loads(action.data)["to"]

    if not current_location:
        return JsonResponse({
            "result": []
        })

    movement_left = get_remaining_train_movement(game_id)
    track = compute_paths_from(game_id=game_id, location=current_location, max_length=movement_left)

    return JsonResponse({
        "result": [{"destination": dest, "path": path} for dest, path in track]
    })
