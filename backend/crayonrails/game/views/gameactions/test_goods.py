from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase, RequestFactory

from . import actiontypes
from .goods import action_good_pickup, action_good_deliver, action_good_dump
from ..utils.gameactions import get_money_for_player, get_current_goods_carried, get_demand_cards_holding
from ...models import Game, PlayerSlot


class GoodPickup(TestCase):
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

        self.player = User.objects.create_user(
            username="regularjoe"
        )

        self.slot = PlayerSlot(game_id=self.game.id, user_id=self.player.id, role="guest")
        self.slot.save()

        self.factory = RequestFactory()

        actiontypes.player_joined(game_id=self.game.id, sequence_number=3, play_order=0, screen_name="player",
                                  player_id=self.slot.id).save()

        actiontypes.start_game(game.id, sequence_number=4).save()

        actiontypes.start_turn(game.id, sequence_number=5, play_order=0).save()

    def test_anonymous(self):
        request = self.factory.post("")

        request.user = AnonymousUser()

        response = action_good_pickup(request, self.game.id, "blah")
        self.assertEqual(response.status_code, 403)

    def test_nonplayer(self):
        request = self.factory.post("")

        request.user = User.objects.create_user("nonplayerjoe")

        response = action_good_pickup(request, self.game.id, "blah")
        self.assertEqual(response.status_code, 403)

    def test_player_nonexistent_good(self):
        request = self.factory.post("")

        request.user = self.player

        response = action_good_pickup(request, self.game.id, "doesnt-exist")
        self.assertEqual(response.status_code, 400)

    def test_player_not_on_supply_of_good(self):
        request = self.factory.post("")

        request.user = self.player

        response = action_good_pickup(request, self.game.id, "stuff")
        self.assertEqual(response.status_code, 400)

    def test_player_in_right_place(self):
        request = self.factory.post("")

        request.user = self.player

        actiontypes.move_train(self.game.id, sequence_number=4, player_id=self.slot.id, location=[5, 6]).save()

        response = action_good_pickup(request, self.game.id, "stuff")
        self.assertEqual(response.status_code, 200)


class GoodDump(TestCase):
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

        self.player = User.objects.create_user(
            username="regularjoe"
        )

        self.slot = PlayerSlot(game_id=self.game.id, user_id=self.player.id, role="guest")
        self.slot.save()

        self.factory = RequestFactory()

        actiontypes.player_joined(game_id=self.game.id, sequence_number=3, play_order=0, screen_name="player",
                                  player_id=self.slot.id).save()

        actiontypes.start_game(game.id, sequence_number=4).save()

        actiontypes.start_turn(game.id, sequence_number=5, play_order=0).save()

    def test_anonymous(self):
        request = self.factory.post("")

        request.user = AnonymousUser()

        response = action_good_dump(request, self.game.id, "blah")
        self.assertEqual(response.status_code, 403)

    def test_nonplayer(self):
        request = self.factory.post("")

        request.user = User.objects.create_user("nonplayerjoe")

        response = action_good_dump(request, self.game.id, "blah")
        self.assertEqual(response.status_code, 403)

    def test_player_nonexistent_good(self):
        request = self.factory.post("")

        request.user = self.player

        response = action_good_dump(request, self.game.id, "doesnt-exist")
        self.assertEqual(response.status_code, 400)

    def test_player_not_on_city(self):
        request = self.factory.post("")

        request.user = self.player

        actiontypes.move_train(self.game.id, sequence_number=4, player_id=self.slot.id, location=[45, 45]).save()

        response = action_good_dump(request, self.game.id, "stuff")
        self.assertEqual(response.status_code, 400)

    def test_player_on_city(self):
        request = self.factory.post("")

        request.user = self.player

        actiontypes.good_pickup(self.game.id, sequence_number=4, player_id=self.slot.id, good="stuff").save()
        actiontypes.move_train(self.game.id, sequence_number=5, player_id=self.slot.id, location=[2, 3]).save()

        response = action_good_dump(request, self.game.id, "stuff")
        self.assertEqual(response.status_code, 200)


class GoodDeliver(TestCase):
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

        self.player = User.objects.create_user(
            username="regularjoe"
        )

        self.slot = PlayerSlot(game_id=self.game.id, user_id=self.player.id, role="guest")
        self.slot.save()

        self.factory = RequestFactory()

        actiontypes.player_joined(game_id=self.game.id, sequence_number=3, play_order=0, screen_name="player",
                                  player_id=self.slot.id).save()

        actiontypes.start_game(game.id, sequence_number=4).save()

        actiontypes.start_turn(game.id, sequence_number=5, play_order=0).save()

    def test_anonymous(self):
        request = self.factory.post("")

        request.user = AnonymousUser()

        response = action_good_deliver(request, self.game.id, "blah", 0)
        self.assertEqual(response.status_code, 403)

    def test_nonplayer(self):
        request = self.factory.post("")

        request.user = User.objects.create_user("nonplayerjoe")

        response = action_good_deliver(request, self.game.id, "blah",  0)
        self.assertEqual(response.status_code, 403)

    def test_player_nonexistent_good(self):
        request = self.factory.post("")

        request.user = self.player

        response = action_good_deliver(request, self.game.id, "doesnt-exist",  0)
        self.assertEqual(response.status_code, 400)

    def test_player_not_on_city(self):
        request = self.factory.post("")

        request.user = self.player

        actiontypes.good_pickup(self.game.id, sequence_number=4, player_id=self.slot.id, good="stuff").save()
        actiontypes.demand_draw(self.game.id, sequence_number=5, player_id=self.slot.id,
                                demands=[{"good": "stuff", "destination": "City Two", "price": "5"}]).save()
        actiontypes.move_train(self.game.id, sequence_number=6, player_id=self.slot.id, location=[45, 45]).save()

        response = action_good_deliver(request, self.game.id, "stuff", 5)
        self.assertEqual(response.status_code, 400)

    def test_player_on_city(self):
        request = self.factory.post("")

        request.user = self.player

        actiontypes.good_pickup(self.game.id, sequence_number=4, player_id=self.slot.id, good="stuff").save()
        actiontypes.demand_draw(self.game.id, sequence_number=5, player_id=self.slot.id,
                                demands=[{"good": "stuff", "destination": "City Two", "price": 5}]).save()
        actiontypes.move_train(self.game.id, sequence_number=6, player_id=self.slot.id, location=[2, 3]).save()

        self.assertEqual(get_demand_cards_holding(self.game.id, self.slot.id), {5})
        self.assertEqual(get_money_for_player(self.game.id, self.slot.id), 0)
        self.assertListEqual(get_current_goods_carried(self.game.id, self.slot.id)["stuff"], [4])

        response = action_good_deliver(request, self.game.id, "stuff", 5)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(get_money_for_player(self.game.id, self.slot.id), 5)

        self.assertListEqual(get_current_goods_carried(self.game.id, self.slot.id)["stuff"], [])

        self.assertEqual(get_demand_cards_holding(self.game.id, self.slot.id), set())

    def test_player_on_city_more_than_one_demand_same_good_same_card(self):
        request = self.factory.post("")

        request.user = self.player

        actiontypes.good_pickup(self.game.id, sequence_number=4, player_id=self.slot.id, good="stuff").save()
        actiontypes.demand_draw(self.game.id, sequence_number=5, player_id=self.slot.id,
                                demands=[{"good": "stuff", "destination": "City Two", "price": 5}, {"good": "stuff", "destination": "City One", "price": 5}]).save()
        actiontypes.move_train(self.game.id, sequence_number=6, player_id=self.slot.id, location=[2, 3]).save()

        self.assertEqual(get_demand_cards_holding(self.game.id, self.slot.id), {5})
        self.assertEqual(get_money_for_player(self.game.id, self.slot.id), 0)
        self.assertListEqual(get_current_goods_carried(self.game.id, self.slot.id)["stuff"], [4])

        response = action_good_deliver(request, self.game.id, "stuff", 5)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(get_money_for_player(self.game.id, self.slot.id), 5)

        self.assertListEqual(get_current_goods_carried(self.game.id, self.slot.id)["stuff"], [])

        self.assertEqual(get_demand_cards_holding(self.game.id, self.slot.id), set())