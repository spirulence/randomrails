from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):
    title = models.CharField(max_length=160)

    def __str__(self):
        return f"Game {self.id} - {self.title}"


class PlayerSlot(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    role = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.id}: Game {self.game_id} - {self.role}"


class Invite(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    code = models.CharField(max_length=100)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Invite to Game {self.game_id}"


class LobbyAccess(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"LobbyAccess for Game {self.game_id} and {self.user}"


class GameAction(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    type = models.CharField(max_length=200)
    sequence_number = models.BigIntegerField()
    data = models.CharField(max_length=255)

    def __str__(self):
        return f"Game {self.game_id} - A{self.sequence_number}:{self.type}"
