from django.test import TransactionTestCase
from django.http import Http404
from srcs_user import services as userServices, models as userModels
from srcs_chat import services as chatServices, models as chatModels
from srcs_user.tests.factories import UserFactory

# Create your tests here.
# @transaction.atomic
class TestUserCase(TransactionTestCase):
    reset_sequences = True
    def tearDown(self):
        UserFactory.reset_sequence()

    def test_find_one_that_exists(self):
        user1 = UserFactory()
        user2 = UserFactory()
        first_user = userServices.find_one(1)
        second_user = userServices.find_one(2)

        self.assertEqual(user1.username, first_user.username)
        self.assertEqual(user2.username, second_user.username)

    def test_find_one_doesnt_exist(self):
        UserFactory()
        self.assertRaises(Http404, userServices.find_one, 2)

    def test_find_all(self):
        total_users = 10
        users = []
        for _ in range(total_users):
            users.append(UserFactory())
        
        all_users = userServices.find_all()
        self.assertEqual(len(all_users), total_users)
        for i in range(total_users):
            self.assertEqual(users[i].username, all_users[i].username)
            self.assertEqual(users[i].description, all_users[i].description)
        
    def test_update(self):
        user = UserFactory()
        current_username = user.username
        user.username = 'cavalinho'
        userServices.update(1, user)
        new_username = userServices.find_one(1).username
        self.assertNotEqual(new_username, current_username)
        self.assertEqual(new_username, 'cavalinho')

    def test_update_when_user_doesnt_exist(self):
        user = UserFactory()
        user.username = 'cavalinho'
        self.assertRaises(Http404, userServices.update, 2, user)

    def test_delete_one(self):
        UserFactory()
        userServices.delete_one(1)
        self.assertEqual(len(userModels.User.objects.all()), 0)

    def test_delete_one_when_user_not_found(self):
        user = UserFactory()

        self.assertRaises(Http404, userServices.delete_one, 2)
        self.assertEqual(user.id, userServices.find_one(1).id)


    def test_compute_mmr_points(self):
        user = UserFactory()
        mmr = user.mmr

        userServices.compute_mmr_points(user.id, 20)
        self.assertEqual(userServices.find_one(1).mmr, mmr + 20)

        userServices.compute_mmr_points(user.id, -20)
        self.assertEqual(userServices.find_one(1).mmr, mmr)

    def test_compute_mmr_points_when_user_not_found(self):
        self.assertRaises(Http404, userServices.compute_mmr_points, 1, 20)
