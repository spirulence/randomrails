from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase, RequestFactory

from .train import action_move_train
from ..utils.gameactions import get_money_for_player
from ...models import Game, PlayerSlot
from . import actiontypes


class MoveTrain(TestCase):
    def setUp(self) -> None:
        game = Game()
        game.save()
        self.game = game

        actiontypes.add_medium_city(game.id, sequence_number=0, name="City One", location=[5, 5],
                                   goods=["stuff", "stuff2"]).save()

        actiontypes.add_mountain(game.id, sequence_number=1, location=[6, 5]).save()

        self.creator = User.objects.create_user(
            username="creatorjoe"
        )
        self.player = User.objects.create_user(
            username="playerjoe"
        )

        self.creator_slot = PlayerSlot(game_id=self.game.id, index=0, user_id=self.creator.id, role="creator")
        self.creator_slot.save()

        self.player_slot = PlayerSlot(game_id=self.game.id, index=1, user_id=self.player.id, role="guest")
        self.player_slot.save()

        self.factory = RequestFactory()

    def test_anonymous(self):
        request = self.factory.post("")

        request.user = AnonymousUser()

        response = action_move_train(request, self.game.id, 5, 5)
        self.assertEqual(response.status_code, 403)

    def test_nonplayer(self):
        request = self.factory.post("")

        request.user = User.objects.create_user("nonplayerjoe")

        response = action_move_train(request, self.game.id, 5, 5)
        self.assertEqual(response.status_code, 403)

    def test_player(self):
        request = self.factory.post("")

        request.user = self.player

        response = action_move_train(request, self.game.id, 5, 5)
        self.assertEqual(response.status_code, 200)