from django.test import TestCase
from .. import services
from .. import models

# Create your tests here.

class TestUserCase(TestCase):
    def setUp(self):
        models.User.objects.create(id=1, username='cavalinho', id42=1234)
        models.User.objects.create(id=2, username='cavalinho2', id42=4321)

    def tearDown(self):
        pass

    def test_find_one(self):
        first_user = services.find_one(1)
        second_user = services.find_one(2)

        self.assertEqual(1234, first_user.id42)
        self.assertEqual(4321, second_user.id42)