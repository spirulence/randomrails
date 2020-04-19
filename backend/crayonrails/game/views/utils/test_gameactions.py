import json

from django.test import TestCase

from ...models import Game, GameAction
from . import gameactions


class TestCurrentTrack(TestCase):

    def setUp(self) -> None:
        self.game = Game()
        self.game.save()

        GameAction(game_id=self.game.id, type="add_track", sequence_number=0,
                   data=json.dumps({
                        "playerId": 0,
                        "from": [1,1],
                        "to": [2,1]
                    })).save()
        GameAction(game_id=self.game.id, type="add_track", sequence_number=1,
                   data=json.dumps({
                       "playerId": 0,
                       "from": [2, 1],
                       "to": [3, 1]
                   })).save()
        GameAction(game_id=self.game.id, type="add_track", sequence_number=2,
                   data=json.dumps({
                       "playerId": 0,
                       "from": [3, 1],
                       "to": [3, 2]
                   })).save()

    def test_simplest_case(self):
        track = gameactions.get_current_track(self.game.id)

        self.assertTrue((3, 1, 3, 2) in track)
        self.assertTrue((2, 1, 3, 1) in track)
        self.assertTrue((1, 1, 2, 1) in track)

    def test_erase(self):
        GameAction(game_id=self.game.id, type="erase_track", sequence_number=3,
                   data=json.dumps({
                       "playerId": 0,
                       "from": [2, 1],
                       "to": [3, 1]
                   })).save()

        track = gameactions.get_current_track(self.game.id)

        self.assertTrue((3, 1, 3, 2) in track)
        self.assertFalse((2, 1, 3, 1) in track)
        self.assertTrue((1, 1, 2, 1) in track)

    def test_erase_rebuild(self):
        GameAction(game_id=self.game.id, type="erase_track", sequence_number=3,
                   data=json.dumps({
                       "playerId": 0,
                       "from": [2, 1],
                       "to": [3, 1]
                   })).save()

        GameAction(game_id=self.game.id, type="add_track", sequence_number=4,
                   data=json.dumps({
                       "playerId": 0,
                       "from": [2, 1],
                       "to": [3, 1]
                   })).save()

        track = gameactions.get_current_track(self.game.id)

        self.assertTrue((3, 1, 3, 2) in track)
        self.assertTrue((2, 1, 3, 1) in track)
        self.assertTrue((1, 1, 2, 1) in track)
