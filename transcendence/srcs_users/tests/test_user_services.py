from django.test import TestCase
# from django.db import transaction
from django.http import Http404
from srcs_users import services, models
from srcs_users.tests.factories import UserFactory

# Create your tests here.
# @transaction.atomic
class TestUserCase(TestCase):

    def tearDown(self):
        UserFactory.reset_sequence()

    def test_find_one_that_exists(self):
        user1 = UserFactory()
        user2 = UserFactory()
        first_user = services.find_one(1)
        second_user = services.find_one(2)

        self.assertEqual(user1.username, first_user.username)
        self.assertEqual(user2.username, second_user.username)

    def test_find_one_doesnt_exist(self):
        UserFactory()
        self.assertRaises(Http404, services.find_one, 2)

    def test_find_all(self):
        total_users = 10
        users = []
        for _ in range(total_users):
            users.append(UserFactory())
        
        all_users = services.find_all()
        self.assertEqual(len(all_users), total_users)
        for i in range(total_users):
            self.assertEqual(users[i].username, all_users[i].username)
            self.assertEqual(users[i].description, all_users[i].description)
        
    def test_update(self):
        user = UserFactory()
        current_username = user.username
        user.username = 'cavalinho'
        services.update(1, user)
        new_username = services.find_one(1).username
        self.assertNotEqual(new_username, current_username)
        self.assertEqual(new_username, 'cavalinho')

    def test_update_when_user_doesnt_exist(self):
        user = UserFactory()
        user.username = 'cavalinho'
        self.assertRaises(Http404, services.update, 2, user)

    def test_delete_one(self):
        UserFactory()
        services.delete_one(1)
        self.assertEqual(len(models.User.objects.all()), 0)

    def test_delete_one_when_user_not_found(self):
        user = UserFactory()

        self.assertRaises(Http404, services.delete_one, 2)
        self.assertEqual(user.id, services.find_one(1).id)

    def test_compute_victory(self):
        user = UserFactory()
        wins = user.wins

        services.compute_victory(user.id)

        self.assertEqual(services.find_one(1).wins, wins + 1)

    def test_compute_victory_when_user_not_found(self):
        self.assertRaises(Http404, services.compute_victory, 1)

    def test_compute_loss(self):
        user = UserFactory()
        loss = user.loss

        services.compute_loss(user.id)

        self.assertEqual(services.find_one(1).loss, loss + 1)

    def test_compute_loss_when_user_not_found(self):
        self.assertRaises(Http404, services.compute_loss, 1)

    def test_compute_experience(self):
        user = UserFactory()
        expGame = user.expGame

        services.compute_experience(user.id, 20)
        self.assertEqual(services.find_one(1).expGame, expGame + 20)

        services.compute_experience(user.id, -20)
        self.assertEqual(services.find_one(1).expGame, expGame)

    def test_compute_experience_when_user_not_found(self):
        self.assertRaises(Http404, services.compute_experience, 1, 20)
