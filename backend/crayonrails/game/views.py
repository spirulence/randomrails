import json
import math
import random
from collections import defaultdict

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST

from .models import Game, GameAction
from .actions import build_new_map, distances

def index(request):
    return HttpResponse("Hello, World. You're at the game index.")

def game_new(request):
    new_game = Game(title="New Game", password="")
    new_game.save()
    new_game.title = f"New Game {new_game.id}"
    new_game.save()

    build_new_map(new_game)

    return redirect(f"/static/?game_id={new_game.id}")


def actions(request, game_id):
    query = GameAction.objects.filter(game_id=game_id).order_by('sequence_number')
    actions_result = [{"sequenceNumber": a.sequence_number, "type": a.type, "data": json.loads(a.data)} for a in query]

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