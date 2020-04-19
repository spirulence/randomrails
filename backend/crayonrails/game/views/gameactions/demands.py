import json
import random

from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views.decorators.http import require_POST

from . import actiontypes
from ..utils import gameactions
from ..utils.gameflow import is_players_turn, get_players_turn
from ..utils.distance import distances
from ..utils.gameactions import last_game_action, get_goods_map, get_cities_map
from ..utils.permissions import is_player
from ...models import GameAction, PlayerSlot


def single_demand(game_id, demand_id):
    goods = get_goods_map(game_id)
    cities = get_cities_map(game_id)
    good = random.choice(list(goods.keys()))
    city = random.choice(list(cities.keys()))
    all_distances = list(distances(cities[city], goods[good]))
    closest = min(all_distances)
    farthest = min(all_distances)
    money = max(5, int((closest + farthest) / 2.1) + random.choice([5, 3, 0, -3, 5]))
    demand = {
        "good": good,
        "destination": city,
        "price": money,
        "id": demand_id
    }
    return demand


@require_POST
def action_demand_draw(request, game_id):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    slot = PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)

    player_demands_drawn = [action for action in
                            GameAction.objects.filter(game_id=game_id, type="demand_draw").order_by('-sequence_number')
                            if json.loads(action.data)["playerId"] == slot.id]
    player_demands_discarded = [action for action in
                                GameAction.objects.filter(game_id=game_id, type="demand_discarded").order_by(
                                    '-sequence_number')
                                if json.loads(action.data)["playerId"] == slot.id]

    if len(player_demands_drawn) >= (len(player_demands_discarded) + 3):
        return HttpResponseBadRequest("already have max number of demand cards")

    # otherwise, generate and save a "draw_demand" action
    next_sequence_number = last_game_action(game_id).sequence_number + 1
    game_action = GameAction(
        game_id=game_id,
        sequence_number=next_sequence_number,
        type="demand_draw",
        data=json.dumps({
            "playerId": slot.id,
            "demandCardId": next_sequence_number,
            "demands": [single_demand(game_id, f"{next_sequence_number}-0"), single_demand(game_id, f"{next_sequence_number}-1"), single_demand(game_id, f"{next_sequence_number}-2")]
        }))
    game_action.save()
    return JsonResponse({
        "result": "success"
    })


@require_POST
def action_demand_discard_all(request, game_id):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    slot = PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)

    if not is_players_turn(request, game_id):
        return HttpResponseBadRequest("it is not your turn")

    player_demands_drawn = [action for action in
                            GameAction.objects.filter(game_id=game_id, type="demand_draw").order_by('-sequence_number')
                            if json.loads(action.data)["playerId"] == slot.id]
    player_demands_discarded = [action for action in
                                GameAction.objects.filter(game_id=game_id, type="demand_discarded").order_by(
                                    '-sequence_number')
                                if json.loads(action.data)["playerId"] == slot.id]

    if len(player_demands_drawn) != (len(player_demands_discarded) + 3):
        return HttpResponseBadRequest("can only discard when you have three cards")

    extant_card_ids = set(d.sequence_number for d in player_demands_drawn)

    for d in player_demands_discarded:
        extant_card_ids.remove(json.loads(d.data)["demandCardId"])

    next_sequence_number = last_game_action(game_id).sequence_number + 1

    for index, card_id in enumerate(extant_card_ids):
        actiontypes.demand_discarded(game_id, sequence_number=next_sequence_number + index, player_id=slot.id, card_id=card_id).save()

    new_play_order = get_players_turn(game_id, request) + 1
    if new_play_order > gameactions.get_max_play_order(game_id):
        new_play_order = 0

    if new_play_order == 0:
        actiontypes.start_round(
            game_id=game_id,
            sequence_number=gameactions.last_game_action(game_id).sequence_number + 1).save()

    actiontypes.start_turn(game_id, sequence_number=gameactions.last_game_action(game_id).sequence_number + 1,
                           play_order=new_play_order).save()

    return JsonResponse({
        "result": "success"
    })