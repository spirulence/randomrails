import pdb

from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_POST

from .gameactions import actiontypes, PlayerSlot
from .utils import gameactions
from .utils.gameflow import is_players_turn, get_players_turn
from .utils.permissions import is_creator, is_player


@require_POST
def start_game(request, game_id):
    if not is_creator(request, game_id):
        return HttpResponseForbidden("you didn't create this game")

    if gameactions.is_started(game_id):
        return HttpResponseBadRequest("game is already started")

    actiontypes.start_game(game_id, sequence_number=gameactions.last_game_action(game_id).sequence_number + 1).save()
    actiontypes.start_round(game_id, sequence_number=gameactions.last_game_action(game_id).sequence_number + 1).save()
    actiontypes.start_turn(game_id, sequence_number=gameactions.last_game_action(game_id).sequence_number + 1, play_order=0).save()

    return JsonResponse({"result": "success"})


@require_POST
def advance_turn(request, game_id):
    if not is_player(request, game_id):
        return HttpResponseForbidden("you aren't in this game")

    if not is_players_turn(game_id, request):
        return HttpResponseBadRequest("it's not your turn right now")

    new_play_order = get_players_turn(game_id, request) + 1
    if new_play_order > gameactions.get_max_play_order(game_id):
        new_play_order = 0

    if new_play_order == 0:
        actiontypes.start_round(
            game_id=game_id,
            sequence_number=gameactions.last_game_action(game_id).sequence_number + 1).save()

    actiontypes.start_turn(game_id, sequence_number=gameactions.last_game_action(game_id).sequence_number + 1,
                           play_order=new_play_order).save()

    return JsonResponse({"result": "success"})
