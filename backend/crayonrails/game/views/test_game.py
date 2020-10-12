import json

from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.sessions.models import Session
from django.test import TestCase, RequestFactory

from .game import game_new, game_join
from ..models import Game, PlayerSlot, GameAction


class GameNew(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.post("/game/new")

    def test_anonymous_user_fails(self):
        self.request.user = AnonymousUser()

        response = game_new(self.request)
        self.assertEqual(response.status_code, 403)

    def test_non_permissioned_user_fails(self):
        self.request.user = User.objects.create_user(
            username="regularjoe"
        )

        response = game_new(self.request)
        self.assertEqual(response.status_code, 403)

class GameJoin(TestCase):

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

        request = self.factory.get("/game/new")

        request.user = User.objects.create_superuser(
            username="regularjoe"
        )

        response = game_new(request)
        _, game_id = response.get("Location").split("?game_id=")

        self.game = Game.objects.get(id=game_id)



