import json

from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase, RequestFactory

from . import actiontypes
from .demands import single_demand, action_demand_draw
from ..utils.gameactions import last_game_action, get_goods_map, get_cities_map
from ...models import Game, PlayerSlot


class Maps(TestCase):
    def setUp(self):
        game = Game()
        game.save()
        self.game = game

        city1 = actiontypes.add_major_city(
            game.id, sequence_number=0, name="City One", location=[1, 1], goods=["stuff", "stuff2"])
        city1.save()

        city2 = actiontypes.add_major_city(
            game.id, sequence_number=1, name="City Two", location=[2, 3], goods=["stuff3"])
        city2.save()

        city3 = actiontypes.add_major_city(
            game.id, sequence_number=2, name="City Three", location=[5, 6], goods=["stuff4", "stuff"])
        city3.save()

        city4 = actiontypes.add_major_city(
            game.id, sequence_number=3, name="City Four", location=[7, 6], goods=[])
        city4.save()

        self.factory = RequestFactory()

    def test_single_demand(self):
        result = single_demand(self.game.id, demand_id=0)
        self.assertIn(result["good"], ["stuff", "stuff2", "stuff3", "stuff4"])

    def test_draw_demand_anonymous(self):
        request = self.factory.post("")

        request.user = AnonymousUser()

        response = action_demand_draw(request, game_id=self.game.id)
        self.assertEqual(response.status_code, 403)

    def test_draw_demand_nonplayer(self):
        request = self.factory.post("")

        request.user = User.objects.create_user(
            username="nonplayerjoe"
        )

        response = action_demand_draw(request, game_id=self.game.id)
        self.assertEqual(response.status_code, 403)

    def test_draw_demand(self):
        request = self.factory.post("")

        request.user = User.objects.create_user(
            username="regularjoe"
        )

        goods = get_goods_map(self.game.id)
        cities = get_cities_map(self.game.id)

        PlayerSlot(game_id=self.game.id, user_id=request.user.id, role="guest").save()

        response = action_demand_draw(request, game_id=self.game.id)
        self.assertEqual(response.status_code, 200)

        game_action = last_game_action(self.game.id)
        game_action_data = json.loads(game_action.data)

        self.assertEqual(game_action.type, "demand_draw")
        self.assertEqual(game_action.type, "demand_draw")
        self.assertEqual(game_action_data["playerId"], 1)
        self.assertEqual(game_action_data["demandCardId"], game_action.sequence_number)
        self.assertEqual(len(game_action_data["demands"]), 3)
        self.assertIn(game_action_data["demands"][0]["good"], goods)
        self.assertIn(game_action_data["demands"][0]["destination"], cities)

    def test_draw_max_demands(self):
        request = self.factory.post("")

        request.user = User.objects.create_user(
            username="regularjoe"
        )

        PlayerSlot(game_id=self.game.id, user_id=request.user.id, role="guest").save()

        self.assertEqual(action_demand_draw(request, game_id=self.game.id).status_code, 200)
        self.assertEqual(action_demand_draw(request, game_id=self.game.id).status_code, 200)
        self.assertEqual(action_demand_draw(request, game_id=self.game.id).status_code, 200)

        self.assertEqual(action_demand_draw(request, game_id=self.game.id).status_code, 400)
