import json
from collections import defaultdict

from ...models import GameAction


def last_game_action(game_id):
    return GameAction.objects.filter(game_id=game_id).order_by('-sequence_number').first()


def get_current_train_location(game_id, player_number):
    for action in GameAction.objects.filter(game_id=game_id, type="move_train").order_by('-sequence_number'):
        if json.loads(action.data)["playerNumber"] == player_number:
            return tuple(json.loads(action.data)["to"])


def get_goods_map(game_id):
    goods_to_locations = defaultdict(list)

    for action in GameAction.objects.filter(game_id=game_id):
        data = json.loads(action.data)
        if "available_goods" in data:
            for good in data["available_goods"]:
                goods_to_locations[good].append(tuple(data["location"]))

    return goods_to_locations


def get_cities_map(game_id):
    cities = {}

    for action in GameAction.objects.filter(game_id=game_id):
        data = json.loads(action.data)
        if "city" in action.type:
            cities[data["name"]] = tuple(data["location"])

    return cities


def get_money_for_player(game_id, player_number):
    actions = GameAction.objects.filter(game_id=game_id, type="adjust_money")
    return sum(json.loads(a.data)["amount"] for a in actions if json.loads(a.data)["playerNumber"] == player_number)


def get_current_goods_carried(game_id, player_number):
    deliver_actions = filter(lambda a: json.loads(a.data)["playerNumber"] == player_number,
                             GameAction.objects.filter(game_id=game_id, type="good_delivered"))
    already_delivered_ids = set(json.loads(da.data)["pickupId"] for da in deliver_actions)

    pickup_actions = filter(lambda a: json.loads(a.data)["playerNumber"] == player_number,
                            GameAction.objects.filter(game_id=game_id, type="good_pickup"))

    goods = defaultdict(list)
    for pickup_action in pickup_actions:
        if pickup_action.sequence_number not in already_delivered_ids:
            good = json.loads(pickup_action.data)["good"]
            goods[good].append(pickup_action.sequence_number)

    return goods


def get_demand_cards_holding(game_id, player_number):
    draw_ids = set(a.sequence_number for a  in filter(lambda a: json.loads(a.data)["playerNumber"] == player_number,
                             GameAction.objects.filter(game_id=game_id, type="demand_draw")))

    discard_ids = set(json.loads(a.data)["demandCardId"]for a in filter(lambda a: json.loads(a.data)["playerNumber"] == player_number,
                          GameAction.objects.filter(game_id=game_id, type="demand_discarded")))

    return draw_ids - discard_ids


def get_existing_track(game_id):
    track = {}

    for action in GameAction.objects.filter(game_id=game_id, type="add_track"):
        data = json.loads(action.data)
        unsorted = [tuple(data["from"]), tuple(data["to"])]
        points = tuple(sorted(unsorted))
        track[points] = data["playerNumber"]

    return track
