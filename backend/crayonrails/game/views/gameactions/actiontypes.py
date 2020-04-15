import json

from ...models import GameAction

serializer = json.dumps


def add_major_city(game_id, sequence_number, name, location, goods):
    return GameAction(game_id=game_id, type="add_major_city", sequence_number=sequence_number, data=serializer({
        "name": name,
        "location": location,
        "available_goods": goods
    }))


def add_medium_city(game_id, sequence_number, name, location, goods):
    return GameAction(game_id=game_id, type="add_medium_city", sequence_number=sequence_number, data=serializer({
        "name": name,
        "location": location,
        "available_goods": goods
    }))


def move_train(game_id, sequence_number, player_id, location):
    return GameAction(
        game_id=game_id,
        sequence_number=sequence_number,
        type="move_train",
        data=serializer({
            "playerId": player_id,
            "to": location
        }))


def good_pickup(game_id, sequence_number, player_id, good):
    return GameAction(
        game_id=game_id,
        sequence_number=sequence_number,
        type="good_pickup",
        data=json.dumps({
            "playerId": player_id,
            "pickupId": sequence_number,
            "good": good
        }))


def good_deliver(game_id, sequence_number, player_id, pickup_id, good):
    return GameAction(
        game_id=game_id,
        sequence_number=sequence_number,
        type="good_delivered",
        data=json.dumps({
            "playerId": player_id,
            "pickupId": pickup_id,
            "good": good
        }))


def money_adjust(game_id, sequence_number, player_id, amount):
    return GameAction(
        game_id=game_id,
        sequence_number=sequence_number,
        type="adjust_money",
        data=json.dumps({
            "playerId": player_id,
            "amount": amount
        }))


def demand_draw(game_id, sequence_number, player_id, demands):
    return GameAction(
        game_id=game_id,
        sequence_number=sequence_number,
        type="demand_draw",
        data=json.dumps({
            "playerId": player_id,
            "demandCardId": sequence_number,
            "demands": demands
        }))


def demand_discarded(game_id, sequence_number, player_id, card_id):
    return GameAction(
        game_id=game_id,
        sequence_number=sequence_number,
        type="demand_discarded",
        data=json.dumps({
            "playerId": player_id,
            "demandCardId": card_id,
        }))


def add_mountain(game_id, sequence_number, location):
    return GameAction(
        game_id=game_id,
        sequence_number=sequence_number,
        type="add_mountain",
        data=json.dumps({
            "location": location
        }))


def player_joined(game_id, sequence_number, player_id, play_order):
    return GameAction(
        game_id=game_id,
        sequence_number=sequence_number,
        type="player_joined",
        data=json.dumps({
            "playerId": player_id,
            "playOrder": play_order
        }))


def player_changed_color(game_id, sequence_number, player_id, new_color):
    return GameAction(
        game_id=game_id,
        sequence_number=sequence_number,
        type="player_changed_color",
        data=json.dumps({
            "playerId": player_id,
            "newColor": new_color
        }))


def add_track(game_id, sequence_number, player_id, track_from, track_to):
    return GameAction(
        game_id=game_id,
        sequence_number=sequence_number,
        type="add_track",
        data=json.dumps({
            "playerId": player_id,
            "from": track_from,
            "to": track_to
        }))