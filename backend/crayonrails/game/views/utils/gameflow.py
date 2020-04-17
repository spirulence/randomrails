from ...models import PlayerSlot
from . import gameactions


def is_players_turn(game_id, request):
    player_turn = get_players_turn(game_id, request)
    current_turn = gameactions.get_current_turn(game_id)
    return player_turn == current_turn


def get_players_turn(game_id, request):
    slot = PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)
    return gameactions.get_play_order_for_player(game_id, slot.id)
