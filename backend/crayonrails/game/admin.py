from django.contrib import admin

from .models import Game, GameAction, PlayerSlot, LobbyAccess, Invite

admin.site.register(Game)
admin.site.register(GameAction)
admin.site.register(PlayerSlot)
admin.site.register(LobbyAccess)
admin.site.register(Invite)
