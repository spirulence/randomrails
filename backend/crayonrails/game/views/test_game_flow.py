import pdb

from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

from .game_flow import start_game, advance_turn
from .gameactions import actiontypes
from ..models import Game, PlayerSlot, GameAction


class StartGame(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

        self.game = Game()
        self.game.save()
        actiontypes.add_medium_city(
            game_id=self.game.id,
            name="City One",
            sequence_number=0,
            location=[5,5],
            goods=[]).save()

        self.creator = User.objects.create_user(
            username="creatorjoe"
        )

        self.creator_slot = PlayerSlot(game_id=self.game.id, user_id=self.creator.id, role="creator")
        self.creator_slot.save()

    def test_nonplayer(self):
        request = self.factory.post("")
        request.user = User.objects.create_user("nonplayer")

        response = start_game(request, self.game.id)
        self.assertEqual(response.status_code, 403)

    def test_start_only_once(self):
        request = self.factory.post("")
        request.user = self.creator

        response = start_game(request, self.game.id)
        self.assertEqual(response.status_code, 200)

        response = start_game(request, self.game.id)
        self.assertEqual(response.status_code, 400)


class AdvanceTurn(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

        self.game = Game()
        self.game.save()

        self.creator = User.objects.create_user(
            username="creatorjoe"
        )

        self.creator_slot = PlayerSlot(game_id=self.game.id, user_id=self.creator.id, role="creator")
        self.creator_slot.save()

        actiontypes.player_joined(game_id=self.game.id, sequence_number=0, play_order=0, screen_name="host", player_id=self.creator_slot.id).save()

        self.player = User.objects.create_user(
            username="playerjoe"
        )

        self.player_slot = PlayerSlot(game_id=self.game.id, user_id=self.player.id, role="guest")
        self.player_slot.save()

        actiontypes.player_joined(game_id=self.game.id, sequence_number=1, play_order=1, screen_name="player", player_id=self.player_slot.id).save()

        actiontypes.start_game(
            game_id=self.game.id,
            sequence_number=2).save()
        actiontypes.start_round(
            game_id=self.game.id,
            sequence_number=3).save()
        actiontypes.start_turn(
            game_id=self.game.id,
            sequence_number=4,
            play_order=0).save()

    def test_nonplayer(self):
        request = self.factory.post("")
        request.user = User.objects.create_user("nonplayer")

        response = advance_turn(request, self.game.id)
        self.assertEqual(response.status_code, 403)

    def test_advance_only_once(self):
        request = self.factory.post("")
        request.user = self.creator

        response = advance_turn(request, self.game.id)
        self.assertEqual(response.status_code, 200)

        response = advance_turn(request, self.game.id)
        self.assertEqual(response.status_code, 400)

    def test_advance_only_on_your_turn(self):
        request = self.factory.post("")
        request.user = self.player

        response = advance_turn(request, self.game.id)
        self.assertEqual(response.status_code, 400)

    def test_advance_starts_new_round(self):
        request = self.factory.post("")
        request.user = self.creator

        response = advance_turn(request, self.game.id)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post("")
        request.user = self.player

        response = advance_turn(request, self.game.id)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(GameAction.objects.filter(type="start_round").all()), 2)
