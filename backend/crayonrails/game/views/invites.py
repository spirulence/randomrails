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
from ..models import Invite, LobbyAccess, PlayerSlot, GameAction


def random_joincode():
    return secrets.token_urlsafe(64)


@require_POST
def invite_create(request, game_id):
    ''' Create an new invite for the user
    Args:
        request: Request with the following parameters
        game_id: Id of the game
    '''
    # Checks if game is already started
    if GameAction.objects.filter(game_id=game_id, type='start_game'):
        return HttpResponseForbidden('Game has already started. You cannot create an invite. Please start a new game.')

    # Checks if the requester is the creator before proceeding
    if not is_creator(request, game_id):
        return HttpResponseForbidden("can't invite people to a game you didn't create")

    # Creates the invite
    invite = Invite(game_id=game_id, code=random_joincode(), expires_at=timezone.now() + datetime.timedelta(minutes=5))
    invite.save()

    # Sends the code for the invite to the requester
    return JsonResponse({
        "result": {"invite": invite.code}
    })


def invite_use(request, game_id, invite_code):
    ''' Allows the requester to join the game with the specified invite_code
    Args:
        request:        Request with the following parameters
        game:           Id of the game requested
        invite_code:    String value that is used to allow the user in the game
    '''

    # Checks if an invite code is not specified returning an error
    if not invite_code:
        return HttpResponseForbidden("<h1>Bad credentials</h1>")

    # Checks if game is already started
    if GameAction.objects.filter(game_id=game_id, type='start_game'):
        return HttpResponseForbidden('Game has already started. You cannot create an invite. Please start a new game.')

    # Attempts to get the invite code from the game
    try:
        invite = Invite.objects.get(game_id=game_id, code=invite_code)
    except Invite.DoesNotExist:

        # Slows down the response time to avoid attacks
        time.sleep(random.uniform(1, 3))
        return HttpResponseForbidden("<h1>Bad credentials</h1>")

    if invite.slot:
        return HttpResponseForbidden("<h1>That's a rejoin code, bruh</h1>")

    # Checks if the invite code has expired
    if invite.expires_at < timezone.now():
        return HttpResponseForbidden("<h1>Invite expired</h1>")

    # Checks if the user is authenticated before adding the user to the lobby and redirecting the game
    # Else create the user and add them to the lobby
    if request.user.is_authenticated:
        try:
            LobbyAccess.objects.get(game_id=game_id, user_id=request.user.id)
        except LobbyAccess.DoesNotExist:
            lobby_access = LobbyAccess(game_id=game_id, user_id=request.user.id)
            lobby_access.save()
        return redirect(f"/static/?game_id={game_id}")
    else:
        user = User.objects.create_user(f"{invite.id}-{game_id}-{secrets.token_hex(8)}")
        lobby_access = LobbyAccess(game_id=game_id, user_id=user.id)
        lobby_access.save()
        login(request, user)
        return redirect(f"/static/?game_id={game_id}")


def rejoin_create(request, game_id, slot_id):
    ''' Allow Users to rejoin the game
    Args:
        request: Request with the following parameters
        game_id: ID of the game
        slot_id: PlayerSlot ID that will be cleared
    '''

    # Checks if the requester is the creator of the game
    if not is_creator(request, game_id):
        return HttpResponseForbidden("Can't rejoin people to a game you didn't create")

    try:
        slot_obj = PlayerSlot.objects.get(id=slot_id)
        if slot_obj.role == "creator":
            return HttpResponseForbidden("Can't rejoin a creator slot")
    except PlayerSlot.DoesNotExist:
        return HttpResponseForbidden("that slot doesn't exist")

    try:
        slot_obj = PlayerSlot.objects.get(id=slot_id)
        slot_obj.user = None
        slot_obj.save()
    except:
        return HttpResponseForbidden('<h1>Unable to create rejoin URL<h1>')

    invite = Invite(
        game_id=game_id, 
        code=random_joincode(), 
        expires_at=timezone.now() + datetime.timedelta(minutes=5),
        slot = slot_obj   
    )
    invite.save()

    return JsonResponse({
        "result": {"invite": invite.code}
    })

    

def invite_rejoin_game(request, game_id, code):

    if not code:
        return HttpResponseForbidden('<h1>Bad Credentials<h1>')
    
    try:
        rejoin_obj = Invite.objects.get(game_id = game_id, code=code)
    except Invite.DoesNotExist:
        time.sleep(random.uniform(1, 3))
        return HttpResponseForbidden('<h1>Bad Credentials<h1>')
    
    if rejoin_obj.expires_at < timezone.now():
        return HttpResponseForbidden('<h1>Invite Expired<h1>')
    
    if request.user.is_authenticated:
        try:
            rejoin_obj.slot.user = request.user
            rejoin_obj.slot.save()
            rejoin_obj.expires_at = timezone.now()
            rejoin_obj.save()
            return redirect(f"/static/?game_id={game_id}")
        except AttributeError as e:
            return HttpResponseForbidden('<h1>Invalid Rejoin URL<h1>')
    else:
        user = User.objects.create_user(f"{rejoin_obj.id}-{game_id}-{secrets.token_hex(8)}")
        rejoin_obj.slot.user = user
        rejoin_obj.slot.save()
        rejoin_obj.expires_at = timezone.now()
        rejoin_obj.save()
        login(request, user)
        return redirect(f"/static/?game_id={game_id}")

