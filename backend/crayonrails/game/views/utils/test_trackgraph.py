import json

from django.test import TestCase

from ...models import GameAction, Game
from .trackgraph import compute_paths_from, get_major_city_track
from ..test_games import complete_game1


class TestPaths(TestCase):

    def setUp(self) -> None:
        self.game = Game()
        self.game.save()

        for action in complete_game1["result"]:
            GameAction(
                game_id=self.game.id,
                type=action["type"],
                sequence_number=action["sequenceNumber"],
                data=json.dumps(action["data"])
            ).save()

    def test_simple(self):
        paths = compute_paths_from(game_id=self.game.id, location=(16, 10))
        self.assertTrue(((16, 20), [(17, 10), (18, 10), (18, 11), (19, 12), (19, 13), (19, 14), (18, 15), (18, 16), (17, 17), (17, 18), (16, 19), (16, 20)]) in paths)
        self.assertTrue(((26, 13), [(17, 10), (18, 10), (18, 11), (19, 12), (19, 13), (20, 13), (21, 13), (22, 13), (23, 13), (24, 13), (25, 13), (26, 13)]) in paths)

    def test_with_major_city_free_track(self):
        paths = compute_paths_from(game_id=self.game.id, location=(9, 22))
        self.assertTrue(((14, 22), [(8, 23), (7, 23), (7, 24), (8, 24), (9, 24), (9, 25), (10, 25), (11, 25), (12, 24), (12, 23), (13, 22), (14, 22)]) in paths)
