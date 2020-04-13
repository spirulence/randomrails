from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase, RequestFactory

from . import actiontypes
from .money import action_adjust_money
from ..utils.gameactions import get_money_for_player, get_current_goods_carried, get_demand_cards_holding
from ...models import Game, PlayerSlot


class AdjustMoney(TestCase):
    def setUp(self) -> None:
        game = Game()
        game.save()
        self.game = game

        actiontypes.add_major_city(game.id, sequence_number=0, name="City One", location=[1, 1], goods=["stuff", "stuff2"]).save()

        self.creator = User.objects.create_user(
            username="creatorjoe"
        )

        self.player = User.objects.create_user(
            username="regularjoe"
        )

        self.creator_slot = PlayerSlot(game_id=self.game.id, index=0, user_id=self.creator.id, role="creator")
        self.creator_slot.save()

        self.slot = PlayerSlot(game_id=self.game.id, index=1, user_id=self.player.id, role="guest")
        self.slot.save()

        self.other_slot = PlayerSlot(game_id=self.game.id, index=2, role="guest")
        self.other_slot.save()

        self.factory = RequestFactory()

    def test_anonymous(self):
        request = self.factory.post("")

        request.user = AnonymousUser()

        response = action_adjust_money(request, self.game.id, self.slot.index, "plus", 5)
        self.assertEqual(response.status_code, 403)

    def test_nonplayer(self):
        request = self.factory.post("")

        request.user = User.objects.create_user("nonplayerjoe")

        response = action_adjust_money(request, self.game.id, self.slot.index, "plus", 5)
        self.assertEqual(response.status_code, 403)

    def test_wrongplayer(self):
        request = self.factory.post("")

        request.user = self.player

        response = action_adjust_money(request, self.game.id, self.other_slot.index, "plus", 5)
        self.assertEqual(response.status_code, 403)

    def test_creator(self):
        request = self.factory.post("")

        request.user = self.creator

        response = action_adjust_money(request, game_id=self.game.id, player=self.other_slot.index, sign="plus", amount=5)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(get_money_for_player(game_id=self.game.id, player_number=self.other_slot.index), 5)

    def test_player_plus(self):
        request = self.factory.post("")

        request.user = self.player

        response = action_adjust_money(request, self.game.id, self.slot.index, "plus", 5)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(get_money_for_player(game_id=self.game.id, player_number=self.slot.index), 5)

    def test_player_minus(self):
        request = self.factory.post("")

        request.user = self.player

        response = action_adjust_money(request, self.game.id, self.slot.index, "minus", 5)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(get_money_for_player(game_id=self.game.id, player_number=self.slot.index), -5)
