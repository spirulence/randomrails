import json

from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_POST

from ..utils.adjacency import are_adjacent
from ..utils.gameactions import get_existing_track
from ..utils.permissions import is_player
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
                            json.loads(action.data)["playerNumber"] == slot.index)
    return sum(json.loads(action.data)["amount"] for action in player_money_actions)


@require_POST
def action_add_track(request, game_id, x1, y1, x2, y2):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    if not are_adjacent((x1, y1), (x2, y2)):
        return HttpResponseBadRequest("points are not adjacent")

    track_key = tuple(sorted([(x1, y1), (x2, y2)]))
    if track_key in get_existing_track(game_id):
        return HttpResponseBadRequest("already track there")

    slot = PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)
    terrain = compute_terrain(game_id)
    cost = compute_track_cost(terrain, x1, y1, x2, y2)
    player_money = get_player_current_money(slot)
    if cost > player_money:
        return HttpResponseBadRequest("you don't have enough money")

    next_sequence_number = GameAction.objects.filter(game_id=game_id).order_by('-sequence_number').first().sequence_number + 1

    money_action = GameAction(
        game_id=game_id,
        sequence_number=next_sequence_number,
        type="adjust_money",
        data=json.dumps({
            "playerNumber": slot.index,
            "amount": -cost
        }))
    money_action.save()

    next_sequence_number += 1

    game_action = GameAction(
        game_id=game_id,
        sequence_number=next_sequence_number,
        type="add_track",
        data=json.dumps({
            "playerNumber": slot.index,
            "from": [x1, y1],
            "to": [x2, y2]
        }))
    game_action.save()
    return JsonResponse({
        "result": "success"
    })