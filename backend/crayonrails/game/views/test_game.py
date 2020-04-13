from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.sessions.models import Session
from django.test import TestCase, RequestFactory

from .game import game_new, game_join
from ..models import Game, PlayerSlot


class GameNew(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_anonymous_user_fails(self):
        request = self.factory.get("/game/new")

        request.user = AnonymousUser()

        response = game_new(request)
        self.assertEqual(response.status_code, 403)

    def test_non_permissioned_user_fails(self):
        request = self.factory.get("/game/new")

        request.user = User.objects.create_user(
            username="regularjoe"
        )

        response = game_new(request)
        self.assertEqual(response.status_code, 403)

    def test_permissioned_user_succeeds(self):
        request = self.factory.get("/game/new")

        request.user = User.objects.create_superuser(
            username="superjoe"
        )

        response = game_new(request)
        self.assertEqual(response.status_code, 302)

    def test_redirect_url(self):
        request = self.factory.get("/game/new")

        request.user = User.objects.create_superuser(
            username="superjoe"
        )

        response = game_new(request)

        self.assertRegexpMatches(response.get("Location"), r"/static/\?game_id\=\d+")

    def test_object_created(self):
        request = self.factory.get("/game/new")

        request.user = User.objects.create_superuser(
            username="superjoe"
        )

        response = game_new(request)
        _, game_id = response.get("Location").split("?game_id=")

        self.assertIsNotNone(Game.objects.get(id=game_id))


class GameJoin(TestCase):

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

        request = self.factory.get("/game/new")

        request.user = User.objects.create_superuser(
            username="regularjoe"
        )

        response = game_new(request)
        _, game_id = response.get("Location").split("?game_id=")

        self.game = Game.objects.get(id=game_id)

    def test_empty_joincode(self):
        request = self.factory.get(f"")
        response = game_join(request, self.game.id, "")

        self.assertEqual(response.status_code, 403)

    def test_wrong_joincode(self):
        request = self.factory.get(f"")
        response = game_join(request, self.game.id, "blah")

        request.user = AnonymousUser()

        self.assertEqual(response.status_code, 403)

    def test_right_joincode(self):
        request = self.factory.get(f"")

        request.user = AnonymousUser()

        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        joincode = PlayerSlot.objects.get(game_id=self.game.id, index=2).joincode
        response = game_join(request, self.game.id, joincode)

        self.assertEqual(response.status_code, 302)

        _, game_id = response.get("Location").split("?game_id=")

        self.assertEqual(int(game_id), self.game.id)

    def test_user_created_for_anonymous_user(self):
        request = self.factory.get(f"")

        request.user = AnonymousUser()

        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        slot = PlayerSlot.objects.get(game_id=self.game.id, index=2)
        self.assertIsNone(slot.user_id)

        game_join(request, self.game.id, slot.joincode)

        slot = PlayerSlot.objects.get(game_id=self.game.id, index=2)
        self.assertIsNotNone(slot.user_id)

    def test_user_linked_for_logged_in_user(self):
        request = self.factory.get(f"")

        request.user = User.objects.create_user("regularjoe-loggedin")

        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        slot = PlayerSlot.objects.get(game_id=self.game.id, index=2)
        self.assertIsNone(slot.user_id)

        game_join(request, self.game.id, slot.joincode)

        slot = PlayerSlot.objects.get(game_id=self.game.id, index=2)
        self.assertEqual(slot.user_id, request.user.id)



