import datetime
import random
import secrets
import time

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .utils.permissions import is_creator
from ..models import Invite, LobbyAccess


def random_joincode():
    return secrets.token_urlsafe(64)


@require_POST
def invite_create(request, game_id):
    if not is_creator(request, game_id):
        return HttpResponseForbidden("can't invite people to a game you didn't create")

    invite = Invite(game_id=game_id, code=random_joincode(), expires_at=timezone.now() + datetime.timedelta(minutes=5))
    invite.save()

    return JsonResponse({
        "result": {"invite": invite.code}
    })


def invite_use(request, game_id, invite_code):
    if not invite_code:
        return HttpResponseForbidden("<h1>Bad credentials</h1>")

    try:
        invite = Invite.objects.get(game_id=game_id, code=invite_code)
    except Invite.DoesNotExist:
        time.sleep(random.uniform(1, 3))
        return HttpResponseForbidden("<h1>Bad credentials</h1>")

    if invite.expires_at < timezone.now():
        return HttpResponseForbidden("<h1>Invite expired</h1>")

    if request.user.is_authenticated:
        try:
            LobbyAccess.objects.get(game_id=game_id, user_id=request.user.id)
        except LobbyAccess.DoesNotExist:
            lobby_access = LobbyAccess(game_id=game_id, user_id=request.user.id)
            lobby_access.save()
        return redirect(f"/static/?game_id={game_id}")
    else:
        user = User.objects.create_user(f"{invite.id}-{game_id}")
        lobby_access = LobbyAccess(game_id=game_id, user_id=user.id)
        lobby_access.save()
        login(request, user)
        return redirect(f"/static/?game_id={game_id}")