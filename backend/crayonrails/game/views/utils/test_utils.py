from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

from .gameactions import get_goods_map, get_cities_map
from ..gameactions import actiontypes
from ...models import Game, PlayerSlot
from .build_player_slots import build_player_slots
from .distance import manhattan_distance, distances
from .adjacency import are_adjacent


class BuildPlayerSlots(TestCase):
    def setUp(self) -> None:
        self.creator = User.objects.create_user("creatorjoe")
        self.game = Game()
        self.game.save()

    def test(self):
        build_player_slots(self.game, self.creator)

        self.assertEqual(len(PlayerSlot.objects.filter(game_id=self.game.id, role="creator")), 1)
        self.assertEqual(len(PlayerSlot.objects.filter(game_id=self.game.id, role="guest")), 5)
        self.assertEqual(len(PlayerSlot.objects.filter(game_id=self.game.id)), 6)
        self.assertListEqual(list(sorted(s.color for s in PlayerSlot.objects.filter(game_id=self.game.id))),
                             ['#0000ff', '#00bfff', '#00ffcc', '#0b8a00', '#bf00ff', '#ffbf00'])
        self.assertEqual(6, len(set(s.joincode for s in PlayerSlot.objects.filter(game_id=self.game.id))))
        self.assertEqual(PlayerSlot.objects.get(game_id=self.game.id, role="creator").joincode, "")


class ManhattanDistance(TestCase):
    def test_list(self):
        self.assertEqual(manhattan_distance([1, 1], [2, 2]), 1)

    def test_tuple(self):
        self.assertEqual(manhattan_distance((1, 1), (2, 2)), 1)

    def test_positive(self):
        self.assertEqual(manhattan_distance((1, 1), (2, 3)), 2)

    def test_negative(self):
        self.assertEqual(manhattan_distance((4, 41), (2, 3)), 38)

    def test_mixed(self):
        self.assertEqual(manhattan_distance((1, 41), (2, 3)), 38)


class Distances(TestCase):
    def test_one(self):
        self.assertListEqual(list(distances([1, 1], [[2, 2]])), [1])

    def test_two(self):
        self.assertListEqual(list(distances([1, 1], [[2, 2], [20, 25]])), [1, 24])


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

    def test_goods_map(self):
        result = get_goods_map(self.game.id)
        self.assertEqual(result, {
            "stuff": [(1, 1), (5, 6)],
            "stuff2": [(1, 1)],
            "stuff3": [(2, 3)],
            "stuff4": [(5, 6)]
        })

    def test_cities_map(self):
        result = get_cities_map(self.game.id)
        self.assertEqual(result, {
            "City One": (1, 1),
            "City Two": (2, 3),
            "City Three": (5, 6),
            "City Four": (7, 6),
        })


class Adjacency(TestCase):
    def test_row_1(self):
        # same row
        self.assertTrue(are_adjacent([1, 1], [2, 1]))
        self.assertTrue(are_adjacent([0, 1], [1, 1]))

        self.assertFalse(are_adjacent([1, 1], [-1, 1]))
        self.assertFalse(are_adjacent([1, 1], [3, 1]))

        # going towards -infinity y
        self.assertTrue(are_adjacent([1, 1], [1, 0]))
        self.assertTrue(are_adjacent([1, 1], [2, 0]))

        self.assertFalse(are_adjacent([1, 1], [0, 0]))
        self.assertFalse(are_adjacent([1, 1], [3, 0]))
        self.assertFalse(are_adjacent([1, 1], [0, -1]))
        self.assertFalse(are_adjacent([1, 1], [1, -1]))
        self.assertFalse(are_adjacent([1, 1], [2, -1]))

        # going towards infinity y
        self.assertTrue(are_adjacent([1, 1], [1, 2]))
        self.assertTrue(are_adjacent([1, 1], [2, 2]))

        self.assertFalse(are_adjacent([1, 1], [0, 3]))
        self.assertFalse(are_adjacent([1, 1], [1, 3]))
        self.assertFalse(are_adjacent([1, 1], [2, 3]))
        self.assertFalse(are_adjacent([1, 1], [3, 3]))
