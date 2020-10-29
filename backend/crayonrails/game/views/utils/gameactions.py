import json
from collections import defaultdict

from .colors import standard_colors
from ...models import GameAction

''' gameactions.py : Game Actions/History that is storeable in the GameActions Table. These actions are queried to return specific pieces information'''

def get_current_track(game_id):
    ''' Gets all Add and Erase track actions performed in the game
    Args:
        game_id: Id of the game
    '''
    
    track = set()   # Ensures only unique track actions are stored

    # Gets all the actions performed that are add or erase track sequentially
    for action in GameAction.objects.filter(game_id=game_id, type__in=["add_track", "erase_track"]).order_by('sequence_number'):

        # Checks action and returns a list of tracks to and from that are stored in json format
        if action.type == "add_track":
            (x1, y1), (x2, y2) = sorted((json.loads(action.data)["from"], json.loads(action.data)["to"]))
            track.add((x1, y1, x2, y2))
        if action.type == "erase_track":
            (x1, y1), (x2, y2) = sorted((json.loads(action.data)["from"], json.loads(action.data)["to"]))
            try:
                track.remove((x1, y1, x2, y2))
            except KeyError:
                pass

    return track

def last_game_action(game_id):
    '''Retrieves the last action performed in the game'''
    return GameAction.objects.filter(game_id=game_id).order_by('-sequence_number').first()


def get_current_train_location(game_id, player_id):
    ''' Gets the current location of the train in the game for the player
    Args:
        game_id: Id of the game
        player_id: Id of the player
    '''
    # Gets the train in the log for the game specified
    for action in GameAction.objects.filter(game_id=game_id, type="move_train").order_by('-sequence_number'):
        if json.loads(action.data)["playerId"] == player_id:
            return tuple(json.loads(action.data)["to"])


def get_goods_map(game_id):
    ''' Gets good locations in the game map
    Args:
        game_id: Id of the game
    '''
    goods_to_locations = defaultdict(list)

    # Fitler the actions performed in the game by available_goods and return all the locations of those goods
    for action in GameAction.objects.filter(game_id=game_id):
        data = json.loads(action.data)
        if "available_goods" in data:
            for good in data["available_goods"]:
                goods_to_locations[good].append(tuple(data["location"]))

    return goods_to_locations


def get_cities_map(game_id):
    ''' Gets all the cities in the map
    Args:
        game_id: Id of the game
    '''
    cities = {}

    # Filter all the actions in the actions in the game and return the location of the cities in the map
    for action in GameAction.objects.filter(game_id=game_id):
        data = json.loads(action.data)
        if "city" in action.type:
            cities[data["name"]] = tuple(data["location"])

    return cities


def get_money_for_player(game_id, player_id):
    ''' Gets the current amount of money a user has in game
    Args:
        game_id: Id of the game
        player_id: Id of the player
    '''
    # Gets all the actions in the game and return the sum of the money adjusted in the game
    actions = GameAction.objects.filter(game_id=game_id, type="adjust_money")
    return sum(json.loads(a.data)["amount"] for a in actions if json.loads(a.data)["playerId"] == player_id)


def get_current_goods_carried(game_id, player_id):

    deliver_actions = filter(lambda a: json.loads(a.data)["playerId"] == player_id,
                             GameAction.objects.filter(game_id=game_id, type="good_delivered"))
    already_delivered_ids = set(json.loads(da.data)["pickupId"] for da in deliver_actions)

    pickup_actions = filter(lambda a: json.loads(a.data)["playerId"] == player_id,
                            GameAction.objects.filter(game_id=game_id, type="good_pickup"))

    goods = defaultdict(list)
    for pickup_action in pickup_actions:
        if pickup_action.sequence_number not in already_delivered_ids:
            good = json.loads(pickup_action.data)["good"]
            goods[good].append(pickup_action.sequence_number)

    return goods


def get_demand_cards_holding(game_id, player_id):
    draw_ids = set(a.sequence_number for a  in filter(lambda a: json.loads(a.data)["playerId"] == player_id,
                             GameAction.objects.filter(game_id=game_id, type="demand_draw")))

    discard_ids = set(json.loads(a.data)["demandCardId"]for a in filter(lambda a: json.loads(a.data)["playerId"] == player_id,
                          GameAction.objects.filter(game_id=game_id, type="demand_discarded")))

    return draw_ids - discard_ids


def get_existing_track(game_id):
    track = {}

    for action in GameAction.objects.filter(game_id=game_id, type="add_track"):
        data = json.loads(action.data)
        unsorted = [tuple(data["from"]), tuple(data["to"])]
        points = tuple(sorted(unsorted))
        track[points] = data["playerId"]

    return track


def get_next_available_play_order(game_id):
    max_play_order = 0

    for action in GameAction.objects.filter(game_id=game_id, type="player_joined"):
        data = json.loads(action.data)
        max_play_order = max(max_play_order, data["playOrder"])

    return max_play_order + 1


def get_color_status(game_id):
    current_in_use = {}

    for action in GameAction.objects.filter(game_id=game_id, type="player_changed_color"):
        data = json.loads(action.data)
        current_in_use[data["playerId"]] = data["newColor"]

    return [{"color": color, "available": color not in current_in_use.values()} for color in standard_colors]


def is_started(game_id):
    try:
        GameAction.objects.get(game_id=game_id, type="start_game")
        return True
    except GameAction.DoesNotExist:
        return False


#TODO: Implement end game logic
def isEnded(game_id):
    pass


def get_current_turn(game_id):
    most_recently_started = GameAction.objects.filter(game_id=game_id, type="start_turn").order_by("-sequence_number").first()
    return json.loads(most_recently_started.data)["playOrder"]


def get_play_order_for_player(game_id, player_id):
    for action in GameAction.objects.filter(game_id=game_id, type="player_joined"):
        data = json.loads(action.data)
        if data["playerId"] == player_id:
            return data["playOrder"]


def get_max_play_order(game_id):
    maximum = 0

    for action in GameAction.objects.filter(game_id=game_id, type="player_joined"):
        data = json.loads(action.data)
        maximum = max(data["playOrder"], maximum)

    return maximum


def get_remaining_train_movement(game_id):
    most_recently_started = GameAction.objects.filter(game_id=game_id, type="start_turn").order_by("-sequence_number").first()

    movement_left = 12
    for action in GameAction.objects.filter(game_id=game_id, type="move_train", sequence_number__gt=most_recently_started.sequence_number):
        movement_left -= json.loads(action.data)["movementUsed"]

    return movement_left


def get_remaining_track_money(game_id):
    most_recently_started = GameAction.objects.filter(game_id=game_id, type="start_turn").order_by(
        "-sequence_number").first()

    money_left = 25
    for action in GameAction.objects.filter(game_id=game_id, type="add_track",
                                            sequence_number__gt=most_recently_started.sequence_number):
        money_left -= json.loads(action.data)["spent"]

    return money_left


def in_water(game_id, x, y):
    water_points = set()
    for water in GameAction.objects.filter(game_id=game_id, type="add_water"):
        water_points.update(tuple(c) for c in json.loads(water.data)["contains"])

    return (x, y) in water_points

