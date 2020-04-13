from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):
    title = models.CharField(max_length=160)

    def __str__(self):
        return f"Game {self.id} - {self.title}"


class PlayerSlot(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    index = models.IntegerField()
    disabled = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    screenname = models.CharField(max_length=255, default="")
    role = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    joincode = models.CharField(max_length=100)

    def __str__(self):
        return f"Game {self.game_id} - P{self.index}:{self.screenname}"


class GameAction(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    type = models.CharField(max_length=200)
    sequence_number = models.BigIntegerField()
    data = models.CharField(max_length=255)

    def __str__(self):
        return f"Game {self.game_id} - A{self.sequence_number}:{self.type}"