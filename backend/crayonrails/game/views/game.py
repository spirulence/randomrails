import base64
import json
import random
import time

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from .utils.permissions import is_player
from .gameactions import actiontypes, last_game_action
from .mapgen.standard import build_new_map
from .utils.gameactions import get_next_available_play_order, get_color_status
from ..models import Game, PlayerSlot, LobbyAccess, GameAction


def game_new(request):
    if request.user.is_authenticated and request.user.has_perm('game.add_game'):
        new_game = Game(title="New Game")
        new_game.save()
        new_game.title = f"New Game {new_game.id}"
        new_game.save()

        build_new_map(new_game)
        slot = PlayerSlot(game_id=new_game.id, user_id=request.user.id, role="creator")
        slot.save()

        actiontypes.player_joined(
            game_id=new_game.id,
            sequence_number=last_game_action(game_id=new_game.id).sequence_number + 1,
            player_id=slot.id,
            play_order=0,
            screen_name="host"
        ).save()
        actiontypes.player_changed_color(
            game_id=new_game.id,
            sequence_number=last_game_action(game_id=new_game.id).sequence_number + 1,
            player_id=slot.id,
            new_color="#00ffcc"
        ).save()

        return JsonResponse({
            "result": {"gameId": new_game.id}
        })
    else:
        return HttpResponseForbidden("<h1>Admins only</h1>")


def game_my_player_id(request, game_id):
    if request.user.is_authenticated:
        try:
            slot = PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)
            return JsonResponse({"result": slot.id})
        except PlayerSlot.DoesNotExist:
            pass
    return HttpResponseForbidden()


def game_my_membership(request, game_id):
    if request.user.is_authenticated:
        try:
            PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)
            return JsonResponse({"result": "joined_game"})
        except PlayerSlot.DoesNotExist:
            pass

        try:
            LobbyAccess.objects.get(game_id=game_id, user_id=request.user.id)
            return JsonResponse({"result": "in_lobby"})
        except LobbyAccess.DoesNotExist:
            pass

    return JsonResponse({"result": "not_a_member"})


def game_lobby_colors_available(request, game_id):
    try:
        LobbyAccess.objects.get(game_id=game_id, user_id=request.user.id)
        return JsonResponse({
            "result": get_color_status(game_id)
        })
    except LobbyAccess.DoesNotExist:
        return HttpResponseForbidden("not a member of that lobby")


@require_POST
def game_join(request, game_id, color, screen_name):
    try:
        LobbyAccess.objects.get(game_id=game_id, user_id=request.user.id)
    except LobbyAccess.DoesNotExist:
        return HttpResponseForbidden("<h1>Bad credentials</h1>")

    color_decoded = str(base64.b64decode(bytes(color, encoding="utf8")), encoding="utf8").lower()

    current_in_use = {}

    for action in GameAction.objects.filter(game_id=game_id, type="player_changed_color"):
        data = json.loads(action.data)
        current_in_use[data["playerId"]] = data["newColor"]

    if color_decoded in current_in_use.values():
        return HttpResponseBadRequest("already a player with that color")

    next_play_order = get_next_available_play_order(game_id)

    slot = PlayerSlot(game_id=game_id, user_id=request.user.id, role="guest")
    slot.save()

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
