import hashlib

from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

from .gameactions import actiontypes
from ..models import Game, PlayerSlot
from .maprender import map_render


class RenderHashTest(TestCase):
    def setUp(self) -> None:
        game = Game()
        game.save()
        self.game = game

        actiontypes.add_medium_city(game.id, sequence_number=0, name="City One", location=[5, 5],
                                    goods=["stuff", "stuff2"]).save()

        actiontypes.add_mountain(game.id, sequence_number=1, location=[6, 5]).save()
        actiontypes.add_mountain(game.id, sequence_number=2, location=[46, 11]).save()

        self.player = User.objects.create_user(
            username="playerjoe"
        )

        self.player_slot = PlayerSlot(game_id=self.game.id, index=1, user_id=self.player.id, role="guest")
        self.player_slot.save()

        self.factory = RequestFactory()

    def test_render(self):
        request = self.factory.get("")

        request.user = self.player

        response = map_render(request, self.game.id)
        self.assertEqual(hashlib.md5(response.content).hexdigest(), 'c183480a2f65a1536c13fda19ad9256d')
