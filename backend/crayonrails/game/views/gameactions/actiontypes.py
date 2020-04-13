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


def move_train(game_id, sequence_number, player_number, location):
    return GameAction(
        game_id=game_id,
        sequence_number=sequence_number,
        type="move_train",
        data=serializer({
            "playerNumber": player_number,
            "to": location
        }))


def good_pickup(game_id, sequence_number, player_number, good):
    return GameAction(
        game_id=game_id,
        sequence_number=sequence_number,
        type="good_pickup",
        data=json.dumps({
            "playerNumber": player_number,
            "pickupId": sequence_number,
            "good": good
        }))


def good_deliver(game_id, sequence_number, player_number, pickup_id, good):
    return GameAction(
        game_id=game_id,
        sequence_number=sequence_number,
        type="good_delivered",
        data=json.dumps({
            "playerNumber": player_number,
            "pickupId": pickup_id,
            "good": good
        }))


def money_adjust(game_id, sequence_number, player_number, amount):
    return GameAction(
        game_id=game_id,
        sequence_number=sequence_number,
        type="adjust_money",
        data=json.dumps({
            "playerNumber": player_number,
            "amount": amount
        }))


def demand_draw(game_id, sequence_number, player_number, demands):
    return GameAction(
        game_id=game_id,
        sequence_number=sequence_number,
        type="demand_draw",
        data=json.dumps({
            "playerNumber": player_number,
            "demandCardId": sequence_number,
            "demands": demands
        }))


def demand_discarded(game_id, sequence_number, player_number, card_id):
    return GameAction(
        game_id=game_id,
        sequence_number=sequence_number,
        type="demand_discarded",
        data=json.dumps({
            "playerNumber": player_number,
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