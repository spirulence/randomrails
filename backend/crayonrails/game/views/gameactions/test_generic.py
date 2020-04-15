import json

from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory

from . import actiontypes
from .generic import actions
from ...models import Game, PlayerSlot


class ActionsAll(TestCase):

    def setUp(self):
        game = Game()
        game.save()
        self.game = game

        city1 = actiontypes.add_medium_city(
            game.id, sequence_number=0, name="City One", location=[1, 1], goods=["stuff", "stuff2"])
        city1.save()

        city2 = actiontypes.add_medium_city(
            game.id, sequence_number=1, name="City Two", location=[5, 6], goods=["stuff3"])
        city2.save()

        self.factory = RequestFactory()

    def test_anonymous(self):
        request = self.factory.get("")

        request.user = AnonymousUser()

        response = actions(request, self.game.id)
        self.assertEqual(response.status_code, 403)

    def test_nonplayer(self):
        request = self.factory.get("")

        request.user = User.objects.create_user("nonplayerjoe")

        response = actions(request, self.game.id)
        self.assertEqual(response.status_code, 403)

    def test_player(self):
        request = self.factory.get("")

        request.user = User.objects.create_user(
            username="regularjoe"
        )

        PlayerSlot(game_id=self.game.id, user_id=request.user.id, role="guest").save()

        response = actions(request, game_id=self.game.id)
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)["result"]
        self.assertEqual(response_data[0]["sequenceNumber"], 0)
        self.assertEqual(response_data[1]["sequenceNumber"], 1)
