from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase, RequestFactory

from .track import action_add_track
from ..utils.gameactions import get_money_for_player
from ...models import Game, PlayerSlot
from . import actiontypes


class AddTrack(TestCase):
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

        self.factory = RequestFactory()

    def test_anonymous(self):
        request = self.factory.post("")

        request.user = AnonymousUser()

        response = action_add_track(request, self.game.id, 5, 5, 6, 5)
        self.assertEqual(response.status_code, 403)

    def test_nonplayer(self):
        request = self.factory.post("")

        request.user = User.objects.create_user("nonplayerjoe")

        response = action_add_track(request, self.game.id, 5, 5, 6, 5)
        self.assertEqual(response.status_code, 403)

    def test_player(self):
        request = self.factory.post("")

        request.user = self.player

        actiontypes.money_adjust(game_id=self.game.id, sequence_number=2, player_id=self.player_slot.id, amount=5).save()

        response = action_add_track(request, self.game.id, 5, 7, 6, 7)
        self.assertEqual(response.status_code, 200)

    def test_non_adjacent(self):
        request = self.factory.post("")

        request.user = self.player

        actiontypes.money_adjust(game_id=self.game.id, sequence_number=2, player_id=self.player_slot.id, amount=5).save()

        response = action_add_track(request, self.game.id, 19, 7, 6, 7)
        self.assertEqual(response.status_code, 400)

    def test_too_expensive(self):
        request = self.factory.post("")

        request.user = self.player

        response = action_add_track(request, self.game.id, 5, 7, 6, 7)
        self.assertEqual(response.status_code, 400)

    def test_clear_mileposts(self):
        request = self.factory.post("")

        request.user = self.player

        actiontypes.money_adjust(game_id=self.game.id, sequence_number=2, player_id=self.player_slot.id,
                                 amount=5).save()
        response = action_add_track(request, self.game.id, 5, 7, 6, 7)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_money_for_player(game_id=self.game.id, player_id=self.player_slot.id), 4)

    def test_unique(self):
        request = self.factory.post("")

        request.user = self.player

        actiontypes.money_adjust(game_id=self.game.id, sequence_number=2, player_id=self.player_slot.id,
                                 amount=5).save()

        response = action_add_track(request, self.game.id, 5, 7, 6, 7)
        self.assertEqual(response.status_code, 200)

        response = action_add_track(request, self.game.id, 6, 7, 5, 7)
        self.assertEqual(response.status_code, 400)

    def test_mountain(self):
        request = self.factory.post("")

        request.user = self.player

        actiontypes.money_adjust(game_id=self.game.id, sequence_number=2, player_id=self.player_slot.id,
                                 amount=5).save()
        response = action_add_track(request, self.game.id, 6, 5, 6, 6)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_money_for_player(game_id=self.game.id, player_id=self.player_slot.id), 3)

    def test_medium_city(self):
        request = self.factory.post("")

        request.user = self.player

        actiontypes.money_adjust(game_id=self.game.id, sequence_number=2, player_id=self.player_slot.id,
                                 amount=5).save()
        response = action_add_track(request, self.game.id, 6, 5, 5, 5)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_money_for_player(game_id=self.game.id, player_id=self.player_slot.id), 3)