import base64
import json

from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase, RequestFactory

from . import game_new, slots_view_all, slots_view_joincodes, slot_view_mine, slot_set_color
from ..models import PlayerSlot


class SlotsViewAll(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        request = self.factory.get("/game/new")

        self.creator = User.objects.create_superuser(
            username="superjoe"
        )
        request.user = self.creator

        _, self.game_id = game_new(request).get("Location").split("?game_id=")
        self.game_id = int(self.game_id)

        self.player = User.objects.create_user("regularjoe")
        slot = PlayerSlot.objects.get(game_id=self.game_id, index=2)
        slot.user_id = self.player.id
        slot.save()

    def test_view_all_anonymous(self):
        request = self.factory.get("")

        request.user = AnonymousUser()

        response = slots_view_all(request, self.game_id)
        self.assertEqual(response.status_code, 403)

    def test_view_all_signed_in_nonplayer(self):
        request = self.factory.get("")

        request.user = User.objects.create_user("alternatejoe")

        response = slots_view_all(request, self.game_id)
        self.assertEqual(response.status_code, 403)

    def test_view_all_player(self):
        request = self.factory.get("")

        request.user = self.player

        response = slots_view_all(request, self.game_id)
        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assertListEqual(list(sorted(content["result"][0].keys())), ["color", "name", "playerNumber"])

    def test_view_all_creator(self):
        request = self.factory.get("")

        request.user = self.creator

        response = slots_view_all(request, self.game_id)
        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assertListEqual(list(sorted(content["result"][0].keys())), ["color", "name", "playerNumber"])


class SlotsViewJoincodes(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        request = self.factory.get("/game/new")

        self.creator = User.objects.create_superuser(
            username="superjoe"
        )
        request.user = self.creator

        _, self.game_id = game_new(request).get("Location").split("?game_id=")
        self.game_id = int(self.game_id)

        self.player = User.objects.create_user("regularjoe")
        slot = PlayerSlot.objects.get(game_id=self.game_id, index=2)
        slot.user_id = self.player.id
        slot.save()

    def test_view_joincodes_anonymous(self):
        request = self.factory.get("")

        request.user = AnonymousUser()

        response = slots_view_joincodes(request, self.game_id)
        self.assertEqual(response.status_code, 403)

    def test_view_joincodes_signed_in_nonplayer(self):
        request = self.factory.get("")

        request.user = User.objects.create_user("alternatejoe")

        response = slots_view_joincodes(request, self.game_id)
        self.assertEqual(response.status_code, 403)

    def test_view_joincodes_player(self):
        request = self.factory.get("")

        request.user = self.player

        response = slots_view_joincodes(request, self.game_id)
        self.assertEqual(response.status_code, 403)

    def test_view_joincodes_creator(self):
        request = self.factory.get("")

        request.user = self.creator

        response = slots_view_joincodes(request, self.game_id)
        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assertListEqual(list(sorted(content["result"][0].keys())), ["color", "joincode", "name", "playerNumber"])


class SlotsViewMine(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        request = self.factory.get("/game/new")

        self.creator = User.objects.create_superuser(
            username="superjoe"
        )
        request.user = self.creator

        _, self.game_id = game_new(request).get("Location").split("?game_id=")
        self.game_id = int(self.game_id)

        self.player = User.objects.create_user("regularjoe")
        slot = PlayerSlot.objects.get(game_id=self.game_id, index=2)
        slot.user_id = self.player.id
        slot.screenname = "regularjoe"
        slot.color = "#445566"
        slot.save()

    def test_view_mine_anonymous(self):
        request = self.factory.get("")

        request.user = AnonymousUser()

        response = slot_view_mine(request, self.game_id)
        self.assertEqual(response.status_code, 403)

    def test_view_mine_signed_in_nonplayer(self):
        request = self.factory.get("")

        request.user = User.objects.create_user("alternatejoe")

        response = slot_view_mine(request, self.game_id)
        self.assertEqual(response.status_code, 403)

    def test_view_mine_player(self):
        request = self.factory.get("")

        request.user = self.player

        response = slot_view_mine(request, self.game_id)
        self.assertEqual(response.status_code, 200)

        self.assertListEqual(
            list(sorted(json.loads(response.content)["result"].keys())),
            ["color", "name", "playerNumber"])
        self.assertEqual(json.loads(response.content)["result"]["name"], "regularjoe")
        self.assertEqual(json.loads(response.content)["result"]["color"], "#445566")


class SlotSetColor(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        request = self.factory.get("/game/new")

        self.creator = User.objects.create_superuser(
            username="superjoe"
        )
        request.user = self.creator

        _, self.game_id = game_new(request).get("Location").split("?game_id=")
        self.game_id = int(self.game_id)

        self.player = User.objects.create_user("regularjoe")
        slot = PlayerSlot.objects.get(game_id=self.game_id, index=2)
        slot.screenname = "regularjoe"
        slot.user_id = self.player.id
        slot.color = "#445566"
        slot.save()

    def test_anonymous(self):
        request = self.factory.post("")

        request.user = AnonymousUser()

        response = slot_set_color(request, self.game_id, 2, str(base64.b64encode(b"#000000"), "utf8"))
        self.assertEqual(response.status_code, 403)

    def test_non_player(self):
        request = self.factory.post("")

        request.user = User.objects.create_user("alternatejoe")

        response = slot_set_color(request, self.game_id, 2, str(base64.b64encode(b"#000000"), "utf8"))
        self.assertEqual(response.status_code, 403)

    def test_player_bad_color(self):
        request = self.factory.post("")

        request.user = self.player

        response = slot_set_color(request, self.game_id, 2, str(base64.b64encode(b"#000000"), "utf8"))
        self.assertEqual(response.status_code, 400)

    def test_player_color_in_use(self):
        request = self.factory.post("")

        request.user = self.player

        response = slot_set_color(request, self.game_id, 2, str(base64.b64encode(b"#ffbf00"), "utf8"))
        self.assertEqual(response.status_code, 400)

    def test_player_good_color(self):
        request = self.factory.post("")

        request.user = self.player

        response = slot_set_color(request, self.game_id, 2, str(base64.b64encode(b"#660066"), "utf8"))
        self.assertEqual(response.status_code, 200)

    def test_player_good_color_weird_capitalization(self):
        request = self.factory.post("")

        request.user = self.player

        response = slot_set_color(request, self.game_id, 2, str(base64.b64encode(b"#9900cC"), "utf8"))
        self.assertEqual(response.status_code, 200)

