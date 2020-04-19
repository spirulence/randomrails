from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase, RequestFactory

from .train import action_move_train
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

        self.creator_slot = PlayerSlot(game_id=self.game.id, user_id=self.creator.id, role="creator")
        self.creator_slot.save()

        self.player_slot = PlayerSlot(game_id=self.game.id, user_id=self.player.id, role="guest")
        self.player_slot.save()

        actiontypes.add_track(game.id, sequence_number=2, track_from=[6, 5], track_to=[5, 5], spent=1, player_id=self.player_slot.id).save()

        actiontypes.player_joined(game_id=self.game.id, sequence_number=3, play_order=0, screen_name="host",
                                  player_id=self.creator_slot.id).save()

        actiontypes.player_joined(game_id=self.game.id, sequence_number=4, play_order=1, screen_name="player",
                                  player_id=self.player_slot.id).save()

        actiontypes.start_game(game.id, sequence_number=5).save()


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

        actiontypes.start_turn(self.game.id, sequence_number=5, play_order=1).save()

        response = action_move_train(request, self.game.id, 5, 5)
        self.assertEqual(response.status_code, 200)