import json

from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase, RequestFactory

from .gameactions import actiontypes
from .invites import invite_create
from ..models import PlayerSlot, Game


class InviteCreate(TestCase):
    def setUp(self) -> None:
        game = Game()
        game.save()
        self.game = game

        actiontypes.add_major_city(game.id, sequence_number=0, name="City One", location=[1, 1],
                                   goods=["stuff", "stuff2"]).save()

        self.creator = User.objects.create_user(
            username="creatorjoe"
        )

        self.player = User.objects.create_user(
            username="regularjoe"
        )

        self.creator_slot = PlayerSlot(game_id=self.game.id, user_id=self.creator.id, role="creator")
        self.creator_slot.save()

        self.slot = PlayerSlot(game_id=self.game.id, user_id=self.player.id, role="guest")
        self.slot.save()

        self.other_slot = PlayerSlot(game_id=self.game.id, role="guest")
        self.other_slot.save()

        self.factory = RequestFactory()

    def test_anonymous(self):
        request = self.factory.post("")

        request.user = AnonymousUser()

        response = invite_create(request, self.game.id)
        self.assertEqual(response.status_code, 403)

    def test_nonplayer(self):
        request = self.factory.post("")

        request.user = User.objects.create_user("nonplayerjoe")

        response = invite_create(request, self.game.id)
        self.assertEqual(response.status_code, 403)

    def test_player(self):
        request = self.factory.post("")

        request.user = self.player

        response = invite_create(request, self.game.id)
        self.assertEqual(response.status_code, 403)

    def test_creator(self):
        request = self.factory.post("")

        request.user = self.creator

        response = invite_create(request, self.game.id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(json.loads(response.content)["result"]["invite"]) > 32)
