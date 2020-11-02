import json

from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory

from .game import game_new, game_my_membership
from ..models import Game, PlayerSlot


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


class GameMembership(TestCase):

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

        request = self.factory.get("/")

        superuser = User.objects.create_superuser(username="superyou")
        self.superuser = superuser
        request.user = superuser

        response = game_new(request)
        _, game_id = response.get("Location").split("?game_id=")

        self.game = Game.objects.get(id=game_id)

    def test_creator(self):
        request = self.factory.get("/")
        request.user = self.superuser

        response = game_my_membership(request, self.game.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["role"], "creator")

    def test_guest(self):
        guest_user = User.objects.create_user(
            username="regularjoe"
        )

        PlayerSlot(game=self.game, user=guest_user, screen_name="Yepme", role="guest").save()

        request = self.factory.get("/")
        request.user = guest_user

        response = game_my_membership(request, self.game.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["role"], "guest")




