import base64
import json
import random
import time
from collections import defaultdict

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseForbidden, HttpResponseBadRequest
from django.views.decorators.http import require_POST

from .models import Game, GameAction, PlayerSlot
from .actions import build_new_map, distances, build_player_slots


def index(request):
    return HttpResponse("Hello, World. You're at the game index.")


def game_new(request):
    if request.user.is_authenticated and request.user.has_perm('game.add_game'):
        new_game = Game(title="New Game")
        new_game.save()
        new_game.title = f"New Game {new_game.id}"
        new_game.save()

        build_new_map(new_game)
        build_player_slots(new_game, creator=request.user)

        return redirect(f"/static/?game_id={new_game.id}")
    else:
        return HttpResponseForbidden("<h1>Admins only</h1>")


def game_join(request, game_id, joincode):
    if not joincode:
        return HttpResponseForbidden("<h1>Bad credentials</h1>")

    slot = PlayerSlot.objects.get(game_id=game_id, joincode=joincode)

    if not slot:
        time.sleep(random.uniform * 3)
        return HttpResponseForbidden("<h1>Bad credentials</h1>")

    if request.user.is_authenticated:
        slot.user = request.user
        slot.save()
        return redirect(f"/static/?game_id={game_id}")

    if not slot.user:
        slot.user = User.objects.create_user(f"{slot.id}-{game_id}")
        slot.save()
        login(request, slot.user)
        return redirect(f"/static/?game_id={game_id}")

    time.sleep(random.uniform * 3)
    return HttpResponseForbidden("<h1>Bad credentials</h1>")


def is_creator(request, game_id):
    return is_player(request, game_id) and PlayerSlot.objects.get(game_id=game_id,
                                                                  user_id=request.user.id).role == "creator"


def slots_view_all(request, game_id):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    slots = []
    for s in PlayerSlot.objects.filter(game_id=game_id):
        slots.append({"playerNumber": s.index, "name": s.screenname, "color": s.color})

    return JsonResponse({
        "result": slots
    })


def slots_view_joincodes(request, game_id):
    if not is_creator(request, game_id):
        return HttpResponseForbidden()

    slots = []
    for s in PlayerSlot.objects.filter(game_id=game_id):
        slots.append({"playerNumber": s.index, "name": s.screenname, "color": s.color, "joincode": s.joincode})

    return JsonResponse({
        "result": slots
    })


def is_player(request, game_id):
    if request.user.is_authenticated and PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id):
        return True


def actions(request, game_id):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    query = GameAction.objects.filter(game_id=game_id).order_by('sequence_number')
    actions_result = [{"sequenceNumber": a.sequence_number, "type": a.type, "data": json.loads(a.data)} for a in query]

    return JsonResponse({
        "result": actions_result
    })


def action_last(request, game_id):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    a = GameAction.objects.filter(game_id=game_id).order_by('-sequence_number').first()
    actions_result = {"sequenceNumber": a.sequence_number, "type": a.type, "data": json.loads(a.data)}

    return JsonResponse({
        "result": actions_result
    })


def goods_map(game_id):
    goods_to_locations = defaultdict(list)

    for action in GameAction.objects.filter(game_id=game_id):
        data = json.loads(action.data)
        if "available_goods" in data:
            for good in data["available_goods"]:
                goods_to_locations[good].append(data["location"])

    return goods_to_locations


def cities_map(game_id):
    cities = {}

    for action in GameAction.objects.filter(game_id=game_id):
        data = json.loads(action.data)
        if "city" in action.type:
            cities[data["name"]] = data["location"]

    return cities


def demand_random(game_id):
    return JsonResponse({
        "result": {
            "demands": [single_demand(game_id), single_demand(game_id), single_demand(game_id)]
        }
    })


def single_demand(game_id):
    goods = goods_map(game_id)
    cities = cities_map(game_id)
    good = random.choice(list(goods.keys()))
    city = random.choice(list(cities.keys()))
    all_distances = list(distances(cities[city], goods[good]))
    closest = min(all_distances)
    farthest = min(all_distances)
    money = max(5, int((closest + farthest) / 2.1) + random.choice([5, 3, 0, -3, 5]))
    demand = {
        "good": good,
        "destination": city,
        "price": money
    }
    return demand


# @require_POST
# def action_add_terrain(request, game_id, x, y, type):
#     existing = GameAction.objects.filter(game_id=game_id).order_by('-sequence_number')[:1]
#     last_sequence_number = existing[0].sequence_number
#     game_action = GameAction(
#         game_id=game_id,
#         sequence_number=last_sequence_number + 1,
#         type="add_mountain",
#         data=json.dumps({
#             "location": [x, y]
#         }))
#     game_action.save()
#     return JsonResponse({
#         "result": "success"
#     })

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
            "playerNumber": slot.index,
            "to": [x, y]
        }))
    game_action.save()
    return JsonResponse({
        "result": "success"
    })


def get_player_current_money(slot):
    player_money_actions = (action for action in GameAction.objects.filter(game_id=slot.game_id, type="adjust_money") if
                            json.loads(action.data)["playerNumber"] == slot.index)
    return sum(json.loads(action.data)["amount"] for action in player_money_actions)


def compute_terrain(game_id):
    mountains = set()
    cities = set()

    for mountain_action in GameAction.objects.filter(game_id=game_id, type="add_mountain"):
        mountains.add(tuple(json.loads(mountain_action.data)["location"]))

    # for city_action in GameAction.objects.filter(game_id=game_id, type="add_major_city"):
    #     x, y = json.loads(city_action.data)["location"]
    #     if y % 2 == 0:
    #         cities.add((x - 1, y - 1))
    #         cities.add((x, y - 1))
    #         cities.add((x + 1, y))
    #         cities.add((x, y + 1))
    #         cities.add((x - 1, y + 1))
    #         cities.add((x - 1, y))
    #     else:
    #         cities.add((x, y - 1))
    #         cities.add((x + 1, y - 1))
    #         cities.add((x + 1, y))
    #         cities.add((x + 1, y + 1))
    #         cities.add((x, y + 1))
    #         cities.add((x - 1, y))

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


@require_POST
def action_add_track(request, game_id, x1, y1, x2, y2):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

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


@require_POST
def action_adjust_money(request, game_id, player, add_amount):
    if not is_creator(request, game_id):
        return HttpResponseForbidden()

    if add_amount <= 0:
        return HttpResponseBadRequest("must add more than zero money")

    next_sequence_number = GameAction.objects.filter(game_id=game_id).order_by('-sequence_number').first().sequence_number + 1

    game_action = GameAction(
        game_id=game_id,
        sequence_number=next_sequence_number,
        type="adjust_money",
        data=json.dumps({
            "playerNumber": player,
            "amount": add_amount
        }))
    game_action.save()
    return JsonResponse({
        "result": "success"
    })


def slot_view_mine(request, game_id):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    slot = PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)

    return JsonResponse({
        "result": {
            "playerNumber": slot.index,
            "screenName": slot.screenname,
            "color": slot.color
        }
    })


def slot_view(request, game_id, player_number):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    slot = PlayerSlot.objects.get(game_id=game_id, index=player_number)

    return JsonResponse({
        "result": {
            "playerNumber": slot.index,
            "screenName": slot.screenname,
            "color": slot.color
        }
    })


@require_POST
def slot_set_color(request, game_id, player_number, color):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    color_decoded = str(base64.b64decode(bytes(color, encoding="utf8")), encoding="utf8").lower()

    options = [
        "#ff4000", "#0B8A00", "#ffbf00", "#00bfff", "#0000ff", "#bf00ff", "#9900cc", "#cc0099", "#660066", "#00ffcc"
    ]

    if not color_decoded.startswith("#") or not len(color_decoded) == 7 or any(
            map(lambda c: c not in "0123456789abcdef", color_decoded[1:])) or color_decoded not in options:
        return HttpResponseBadRequest()

    slot = PlayerSlot.objects.get(game_id=game_id, index=player_number)
    conflict_slots = PlayerSlot.objects.filter(game_id=game_id, color=color_decoded)[:1]

    if is_creator(request, game_id) or slot.user_id == request.user_id and not conflict_slots:
        slot.color = color_decoded
        slot.save()
        return JsonResponse({
            "result": "success"
        })
    else:
        return HttpResponseBadRequest("can't alter that user's color or it is already in use")


@require_POST
def action_demand_draw(request, game_id):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    slot = PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)
    player_number = slot.index

    player_demands_drawn = [action for action in
                            GameAction.objects.filter(game_id=game_id, type="demand_draw").order_by('-sequence_number')
                            if json.loads(action.data)["playerNumber"] == player_number]
    player_demands_completed = [action for action in
                                GameAction.objects.filter(game_id=game_id, type="demand_complete").order_by(
                                    '-sequence_number')
                                if json.loads(action.data)["playerNumber"] == player_number]
    player_demands_discarded = [action for action in
                                GameAction.objects.filter(game_id=game_id, type="demand_discarded").order_by(
                                    '-sequence_number')
                                if json.loads(action.data)["playerNumber"] == player_number]

    if len(player_demands_drawn) >= (len(player_demands_completed) + len(player_demands_discarded) + 3):
        return HttpResponseBadRequest("already have max number of demand cards")

    # otherwise, generate and save a "draw_demand" action
    next_sequence_number = GameAction.objects.filter(game_id=game_id).order_by('-sequence_number').first().sequence_number + 1
    game_action = GameAction(
        game_id=game_id,
        sequence_number=next_sequence_number,
        type="demand_draw",
        data=json.dumps({
            "playerNumber": player_number,
            "demandCardId": next_sequence_number,
            "demands": [single_demand(game_id), single_demand(game_id), single_demand(game_id)]
        }))
    game_action.save()
    return JsonResponse({
        "result": "success"
    })


@require_POST
def action_good_pickup(request, game_id, good_id):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    slot = PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)
    player_number = slot.index

    next_sequence_number = GameAction.objects.filter(game_id=game_id).order_by('-sequence_number').first().sequence_number + 1
    game_action = GameAction(
        game_id=game_id,
        sequence_number=next_sequence_number,
        type="good_pickup",
        data=json.dumps({
            "playerNumber": player_number,
            "pickupId": next_sequence_number,
            "good": good_id
        }))
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

    deliver_actions = list(
        filter(lambda a: json.loads(a.data)["playerNumber"] == player_number and json.loads(a.data)["good"] == good_id,
               GameAction.objects.filter(game_id=game_id, type="good_delivered")))
    already_delivered_ids = set([json.loads(da.data)["pickupId"] for da in deliver_actions])

    pickup_actions = list(
        filter(lambda a: json.loads(a.data)["playerNumber"] == player_number and json.loads(a.data)["good"] == good_id,
               GameAction.objects.filter(game_id=game_id, type="good_pickup")))

    available_to_dump = [pa for pa in pickup_actions if pa.sequence_number not in already_delivered_ids]

    if len(available_to_dump) == 0:
        return HttpResponseBadRequest("no good of that type to dump")

    next_sequence_number = GameAction.objects.filter(game_id=game_id).order_by('-sequence_number').first().sequence_number + 1

    game_action = GameAction(
        game_id=game_id,
        sequence_number=next_sequence_number,
        type="good_delivered",
        data=json.dumps({
            "playerNumber": player_number,
            "pickupId": pickup_actions[0].sequence_number,
            "good": good_id
        }))
    game_action.save()

    return JsonResponse({
        "result": "success"
    })

@require_POST
def action_good_deliver(request, game_id, good_id, card_id):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    slot = PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)
    player_number = slot.index

    card_action = GameAction.objects.get(game_id=game_id, sequence_number=card_id)
    price = 0
    for demand in json.loads(card_action.data)["demands"]:
        if demand["good"] == good_id:
            price = demand["price"]

    deliver_actions = list(filter(lambda a: json.loads(a.data)["playerNumber"] == player_number and json.loads(a.data)["good"]==good_id,
                               GameAction.objects.filter(game_id=game_id, type="good_delivered")))
    already_delivered_ids = set([json.loads(da.data)["pickupId"] for da in deliver_actions])

    pickup_actions = list(filter(lambda a: json.loads(a.data)["playerNumber"] == player_number and json.loads(a.data)["good"]==good_id,
                           GameAction.objects.filter(game_id=game_id, type="good_pickup")))

    available_to_deliver = [pa for pa in pickup_actions if pa.sequence_number not in already_delivered_ids]

    if len(available_to_deliver) == 0:
        return HttpResponseBadRequest("no good of that type to deliver")

    next_sequence_number = GameAction.objects.filter(game_id=game_id).order_by('-sequence_number').first().sequence_number + 1

    money_action = GameAction(
        game_id=game_id,
        sequence_number=next_sequence_number,
        type="adjust_money",
        data=json.dumps({
            "playerNumber": slot.index,
            "amount": price
        }))
    money_action.save()

    next_sequence_number += 1

    game_action = GameAction(
        game_id=game_id,
        sequence_number=next_sequence_number,
        type="demand_discarded",
        data=json.dumps({
            "playerNumber": player_number,
            "demandCardId": card_action.sequence_number,
        }))
    game_action.save()

    next_sequence_number += 1

    game_action = GameAction(
        game_id=game_id,
        sequence_number=next_sequence_number,
        type="good_delivered",
        data=json.dumps({
            "playerNumber": player_number,
            "pickupId": pickup_actions[0].sequence_number,
            "good": good_id
        }))
    game_action.save()

    return JsonResponse({
        "result": "success"
    })
