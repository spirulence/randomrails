from ...models import PlayerSlot


def is_player(request, game_id):
    if not request.user.id:
        return False
    try:
        slot = PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)
        return request.user.is_authenticated and slot
    except PlayerSlot.DoesNotExist:
        return False


def is_creator(request, game_id):
    if not request.user.id:
        return False
    try:
        slot = PlayerSlot.objects.get(game_id=game_id, user_id=request.user.id)
        return request.user.is_authenticated and slot.role == "creator"
    except PlayerSlot.DoesNotExist:
        return False