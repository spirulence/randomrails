import json

from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_POST

from . import actiontypes
from ..utils.gameflow import is_players_turn
from ..utils.adjacency import are_adjacent
from ..utils.gameactions import get_existing_track, get_remaining_track_money, get_current_track, in_water
from ..utils.permissions import is_player, is_creator
from ...models import PlayerSlot, GameAction


def compute_terrain(game_id):
    mountains = set()
    cities = set()

    for mountain_action in GameAction.objects.filter(game_id=game_id, type="add_mountain"):
        mountains.add(tuple(json.loads(mountain_action.data)["location"]))

    for city_action in GameAction.objects.filter(game_id=game_id, type="add_medium_city"):
        cities.add(tuple(json.loads(city_action.data)["location"]))

    for city_action in GameAction.objects.filter(game_id=game_id, type="add_small_city"):
        cities.add(tuple(json.loads(city_action.data)["location"]))

    return {
        "mountains": mountains,
        "cities": cities
    }


def compute_track_cost(terrain, x1, y1, x2, y2):
    l1 = (x1, y1)
    l2 = (x2, y2)

    if l1 in terrain["cities"] or l2 in terrain["cities"]:
        return 2
    if l1 in terrain["mountains"] or l2 in terrain["mountains"]:
        return 2

    return 1


def get_player_current_money(slot):
    player_money_actions = (action for action in GameAction.objects.filter(game_id=slot.game_id, type="adjust_money") if
                            json.loads(action.data)["playerId"] == slot.id)
    return sum(json.loads(action.data)["amount"] for action in player_money_actions)


@require_POST
def action_add_track(request, game_id, x1, y1, x2, y2):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    if not is_players_turn(request, game_id):
        return HttpResponseBadRequest("it is not your turn")

    if not are_adjacent((x1, y1), (x2, y2)):
        return HttpResponseBadRequest("points are not adjacent")

    if in_water(game_id, x1, y1) or in_water(game_id, x2, y2):
        return HttpResponseBadRequest("can't build on the water")

    track_key = tuple(sorted([(x1, y1), (x2, y2)]))
    if track_key in get_current_track(game_id):
        return HttpResponseBadRequest("already track there")

    slot = PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)
    terrain = compute_terrain(game_id)
    cost = compute_track_cost(terrain, x1, y1, x2, y2)
    player_money = get_player_current_money(slot)
    if cost > player_money:
        return HttpResponseBadRequest("you don't have enough money")

    if cost > get_remaining_track_money(game_id):
        return HttpResponseBadRequest("you don't have enough track building allowance")

    next_sequence_number = GameAction.objects.filter(game_id=game_id).order_by('-sequence_number').first().sequence_number + 1

    money_action = actiontypes.money_adjust(
        game_id=game_id,
        sequence_number=next_sequence_number,
        player_id=slot.id,
        amount=-cost
    )
    money_action.save()

    next_sequence_number += 1

    game_action = actiontypes.add_track(
        game_id=game_id,
        sequence_number=next_sequence_number,
        player_id=slot.id,
        spent=cost,
        track_from=[x1, y1],
        track_to=[x2, y2]
    )
    game_action.save()
    return JsonResponse({
        "result": "success"
    })


@require_POST
def action_erase_track(request, game_id, x1, y1, x2, y2):
    if not is_creator(request, game_id):
        return HttpResponseForbidden()

    if not are_adjacent((x1, y1), (x2, y2)):
        return HttpResponseBadRequest("points are not adjacent")

    track_key = tuple(sorted([(x1, y1), (x2, y2)]))
    if track_key not in get_current_track(game_id):
        return HttpResponseBadRequest("no track there")

    slot = PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)

    next_sequence_number = GameAction.objects.filter(game_id=game_id).order_by('-sequence_number').first().sequence_number + 1

    # money_action = actiontypes.money_adjust(
    #     game_id=game_id,
    #     sequence_number=next_sequence_number,
    #     player_id=slot.id,
    #     amount=+cost
    # )
    # money_action.save()
    #
    # next_sequence_number += 1

    game_action = actiontypes.erase_track(
        game_id=game_id,
        sequence_number=next_sequence_number,
        player_id=slot.id,
        track_from=[x1, y1],
        track_to=[x2, y2]
    )
    game_action.save()
    return JsonResponse({
        "result": "success"
    })


@require_POST
def action_undo_last_track(request, game_id):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    if not is_players_turn(request, game_id):
        return HttpResponseBadRequest("it is not your turn")

    slot = PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)

    last_action = GameAction.objects.filter(game_id=game_id).order_by('-sequence_number').first()

    if last_action.type != "add_track":
        return HttpResponseBadRequest("can only undo track if it is the last action taken")

    next_sequence_number = last_action.sequence_number + 1

    money_action = actiontypes.money_adjust(
        game_id=game_id,
        sequence_number=next_sequence_number,
        player_id=slot.id,
        amount=json.loads(last_action.data)["spent"]
    )
    money_action.save()

    next_sequence_number += 1

    game_action = actiontypes.erase_track(
        game_id=game_id,
        sequence_number=next_sequence_number,
        player_id=slot.id,
        track_from=json.loads(last_action.data)["from"],
        track_to=json.loads(last_action.data)["to"]
    )
    game_action.save()
    return JsonResponse({
        "result": "success"
    })