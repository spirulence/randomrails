import base64
import json

from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from .gameactions import actiontypes, last_game_action
from .mapgen.countries import build_new_map
from .utils.gameactions import get_next_available_play_order, get_color_status
from ..models import Game, PlayerSlot, LobbyAccess, GameAction

#TODO: Allow the user to create a game with a Game Name already specified
def game_new(request):
    ''' Creates a new game
    Args:
        request: Request with following parameters
            - user
    '''

    # If the user is authenticated and has the permission to add a game (Admins only)
    # Otherwise send a forbidden page to the requester
    if request.user.is_authenticated and request.user.has_perm('game.add_game'):
        
        # Creates the Game in the following syntax New Game {game_id}
        new_game = Game(title="New Game")
        new_game.save()
        new_game.title = f"New Game {new_game.id}"
        new_game.save()

        # Builds the map for the game
        build_new_map(new_game)
        slot = PlayerSlot(game_id=new_game.id, user_id=request.user.id, role="creator")
        slot.save()

        # Sets the log to say the player joined the game
        actiontypes.player_joined(
            game_id=new_game.id,
            sequence_number=last_game_action(game_id=new_game.id).sequence_number + 1,
            player_id=slot.id,
            play_order=0,
            screen_name="host"
        ).save()

        # Sets the creator to a default color for the creator
        actiontypes.player_changed_color(
            game_id=new_game.id,
            sequence_number=last_game_action(game_id=new_game.id).sequence_number + 1,
            player_id=slot.id,
            new_color="#00ffcc"
        ).save()

        # redirects the player to the new game
        return redirect(f"/static/index.html?game_id={new_game.id}")
    else:
        return HttpResponseForbidden("<h1>Admins only</h1>")

#TODO: This is really 'get_player_slot_position' within game
def game_my_player_id(request, game_id):
    ''' Gets the player ID within the game's slot
    Args:
        request: request with the following parameters
            - User
                - id
        game_id: Id of the game 
    '''
    if request.user.is_authenticated:

        # Attempts to get user within the Game's player slot 
        try:
            slot = PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)
            return JsonResponse({"result": slot.id})
        except PlayerSlot.DoesNotExist:
            pass
    
    return HttpResponseForbidden()


def game_my_membership(request, game_id):
    ''' Get's player's status in game
    Args:
        request: Request containing the following parameters:
            - user
                - id 
        game_id: Id of the game
    '''

    # Checks if the user is authenticated before proceeding
    if request.user.is_authenticated:
        try:
            # Checks the Game's Player slot to see if the player is joined
            PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)
            return JsonResponse({"result": "joined_game"})
        except PlayerSlot.DoesNotExist:
            pass

        try:
            # Checks the lobby to see for user
            LobbyAccess.objects.get(game_id=game_id, user_id=request.user.id)
            return JsonResponse({"result": "in_lobby"})
        except LobbyAccess.DoesNotExist:
            pass

    return JsonResponse({"result": "not_a_member"})


def game_lobby_colors_available(request, game_id):
    ''' Gets all the colors available in the lobby
    Args:
        request: Request with the following parameters:
            - user
                - id
        game_id: Id of the game
    '''

    # Attempts to get the user within the lobby
    try:
        LobbyAccess.objects.get(game_id=game_id, user_id=request.user.id)
        return JsonResponse({
            "result": get_color_status(game_id)     # Compares the colors retrieved from the lobby to the colors available
        })
    except LobbyAccess.DoesNotExist:
        return HttpResponseForbidden("not a member of that lobby")


@require_POST
def game_join(request, game_id, color, screen_name):
    ''' Allows the requester to join an existing game
    Args:
        request:        Request with the following parameters
        game_id:        Game id of the requester
        color:          Color of the player
        screen_name:    Display Name of the player
    '''

    # Checks if user exists in game
    try:
        LobbyAccess.objects.get(game_id=game_id, user_id=request.user.id)
    except LobbyAccess.DoesNotExist:
        return HttpResponseForbidden("<h1>Bad credentials</h1>")

    # Decods the color specified
    color_decoded = str(base64.b64decode(bytes(color, encoding="utf8")), encoding="utf8").lower()

    current_in_use = {}

    # Checks if the color is already taken
    for action in GameAction.objects.filter(game_id=game_id, type="player_changed_color"):
        data = json.loads(action.data)
        current_in_use[data["playerId"]] = data["newColor"]
    if color_decoded in current_in_use.values():
        return HttpResponseBadRequest("already a player with that color")

    # Adds player to the turn queue
    next_play_order = get_next_available_play_order(game_id)
    slot = PlayerSlot(game_id=game_id, user_id=request.user.id, role="guest", screen_name=screen_name)
    slot.save()

    # Notifies that the player has join the game and color has changed
    actiontypes.player_joined(
        game_id=game_id,
        sequence_number=last_game_action(game_id=game_id).sequence_number + 1,
        player_id=slot.id,
        play_order=next_play_order,
        screen_name=screen_name
    ).save()
    actiontypes.player_changed_color(
        game_id=game_id,
        sequence_number=last_game_action(game_id=game_id).sequence_number + 1,
        player_id=slot.id,
        new_color=color_decoded
    ).save()

    return JsonResponse({
        "result": "success"
    })
