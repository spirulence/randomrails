import json
import random
import time
from collections import defaultdict

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseForbidden
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
    return is_player(request, game_id) and PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id).role == "creator"


def game_view_slots(request, game_id):
    if not is_creator(request, game_id):
        return HttpResponseForbidden()

    slots = []
    for s in PlayerSlot.objects.filter(game_id=game_id):
        if s.role != "creator":
            slots.append({"name": s.screenname, "color": s.color, "joincode": s.joincode})

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

    query = GameAction.objects.filter(game_id=game_id).order_by('-sequence_number')
    actions_result = [{"sequenceNumber": a.sequence_number, "type": a.type, "data": json.loads(a.data)} for a in query]

    return JsonResponse({
        "result": actions_result[0]
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


def demand_random(request, game_id):
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
def action_move_train(request, game_id, color, x, y):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    existing = GameAction.objects.filter(game_id=game_id).order_by('-sequence_number')[:1]
    last_sequence_number = existing[0].sequence_number
    game_action = GameAction(
        game_id=game_id,
        sequence_number=last_sequence_number + 1,
        type="move_train",
        data=json.dumps({
            "color": color,
            "to": [x, y]
        }))
    game_action.save()
    return JsonResponse({
        "result": "success"
    })


@require_POST
def action_add_track(request, game_id, color, x1, y1, x2, y2):
    if not is_player(request, game_id):
        return HttpResponseForbidden()

    existing = GameAction.objects.filter(game_id=game_id).order_by('-sequence_number')[:1]
    last_sequence_number = existing[0].sequence_number
    game_action = GameAction(
        game_id=game_id,
        sequence_number=last_sequence_number + 1,
        type="add_track",
        data=json.dumps({
            "color": color,
            "from": [x1, y1],
            "to": [x2, y2]
        }))
    game_action.save()
    return JsonResponse({
        "result": "success"
    })