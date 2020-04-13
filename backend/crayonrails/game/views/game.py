import random
import time

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

from .mapgen.standard import build_new_map
from .utils.build_player_slots import build_player_slots
from ..models import Game, PlayerSlot


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

    try:
        slot = PlayerSlot.objects.get(game_id=game_id, joincode=joincode)
    except PlayerSlot.DoesNotExist:
        time.sleep(random.uniform(1, 3))
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