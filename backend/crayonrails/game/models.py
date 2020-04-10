from django.db import models


class Game(models.Model):
    title = models.CharField(max_length=160)
    password = models.CharField(max_length=64)


class GameAction(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    type = models.CharField(max_length=200)
    sequence_number = models.BigIntegerField()
    data = models.CharField(max_length=255)
