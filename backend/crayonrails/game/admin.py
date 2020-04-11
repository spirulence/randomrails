from django.contrib import admin

from .models import Game, GameAction, PlayerSlot

admin.site.register(Game)
admin.site.register(GameAction)
admin.site.register(PlayerSlot)
