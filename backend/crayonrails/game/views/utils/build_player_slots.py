import secrets

from ...models import PlayerSlot


def random_joincode():
    return secrets.token_urlsafe(32)


def build_player_slots(game, creator):
    options = [
        "#00ffcc", "#0b8a00", "#ffbf00", "#00bfff", "#0000ff", "#bf00ff", "#9900cc", "#cc0099", "#660066",
    ]

    PlayerSlot(game_id=game.id, user_id=creator.id, color=options[0], role="creator", index=1).save()
    [PlayerSlot(game_id=game.id, color=options[i+1], joincode=random_joincode(), role="guest", index=i+2).save() for i in range(5)]