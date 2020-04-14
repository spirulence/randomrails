import json
from collections import defaultdict

from django.http import HttpResponseForbidden, JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST

from . import actiontypes
from ..utils.gameactions import get_current_train_location, get_goods_map, last_game_action, get_cities_map, \
    get_current_goods_carried
from ..utils.permissions import is_player
from ...models import PlayerSlot, GameAction


@require_POST
def action_good_pickup(request, game_id, good_id):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    slot = PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)
    player_number = slot.index

    current_location = get_current_train_location(game_id, player_number)
    goods_map = get_goods_map(game_id)

    if good_id not in goods_map or current_location not in goods_map[good_id]:
        return HttpResponseBadRequest("good not available at your current location")

    next_sequence_number = last_game_action(game_id).sequence_number + 1
    game_action = actiontypes.good_pickup(game_id, next_sequence_number, player_number, good_id)
    game_action.save()

    return JsonResponse({
        "result": "success"
    })


@require_POST
def action_good_dump(request, game_id, good_id):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    slot = PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)
    player_number = slot.index

    available_to_dump = get_current_goods_carried(game_id, player_number)[good_id]

    if not available_to_dump:
        return HttpResponseBadRequest("no good of that type to dump")

    next_sequence_number = last_game_action(game_id).sequence_number + 1

    actiontypes.good_deliver(game_id, next_sequence_number, player_number, available_to_dump[0], good_id).save()

    return JsonResponse({
        "result": "success"
    })


@require_POST
def action_good_deliver(request, game_id, good_id, card_id):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    slot = PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)
    player_number = slot.index

    try:
        card_action = GameAction.objects.get(game_id=game_id, type="demand_draw", sequence_number=card_id)
    except GameAction.DoesNotExist:
        return HttpResponseBadRequest("that demand card doesn't exist")

    possible_demands = dict((d["destination"], d["price"]) for d in json.loads(card_action.data)["demands"] if d["good"] == good_id)

    if possible_demands is None:
        return HttpResponseBadRequest("that demand card doesn't have a destination for that good")

    current_location = get_current_train_location(game_id, player_number)
    cities = [name for name, location in get_cities_map(game_id).items() if location == current_location]

    if not cities or cities[0] not in possible_demands:
        return HttpResponseBadRequest("you're not at the destination")

    city = cities[0]

    price = possible_demands[city]

    pickup_ids_available_to_deliver = get_current_goods_carried(game_id, player_number)[good_id]

    if not pickup_ids_available_to_deliver:
        return HttpResponseBadRequest("no good of that type to deliver")

    pickup_id = pickup_ids_available_to_deliver[0]

    next_sequence_number = last_game_action(game_id).sequence_number + 1

    actiontypes.money_adjust(game_id, next_sequence_number, player_number, price).save()

    next_sequence_number += 1

    actiontypes.demand_discarded(game_id, next_sequence_number, player_number, card_action.sequence_number).save()

    next_sequence_number += 1

    actiontypes.good_deliver(game_id, next_sequence_number, player_number, pickup_id, good_id).save()

    return JsonResponse({
        "result": "success"
    })
