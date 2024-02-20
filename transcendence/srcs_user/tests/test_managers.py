from django.test import TestCase
from django.contrib.auth import get_user_model

class IntraUserOAuth2ManagerTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.manager = self.User.objects

    def test_create_new_intra_user(self):
        user_data = {
            'id': '123',
            'login': 'testuser',
            'email': 'testuser@example.com',
            'image': {'link': 'https://example.com/avatar.jpg'}
        }

        new_user = self.manager.create_new_intra_user(user_data)

        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.id_42, user_data['id'])
        self.assertEqual(new_user.username, user_data['login'])
        self.assertEqual(new_user.email, user_data['email'])
        self.assertEqual(new_user.avatar, user_data['image']['link'])

    def test_create_superuser(self):
        email = 'admin@example.com'
        username = 'admin' 
        password = 'adminpassword'
            
        superuser = self.manager.create_superuser(email=email, username=username, password=password)


        self.assertIsNotNone(superuser)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertEqual(superuser.email, email)
        self.assertEqual(superuser.username, username)

    def test_create_superuser_existing_user(self):
        existing_user = self.manager.create_user(
            username='admin',
            email='admin@example.com',
            password='password'
        )

        superuser_data = {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'adminpassword'
        }
        

        superuser = self.manager.create_superuser(**superuser_data)

        self.assertIsNotNone(superuser)
        self.assertEqual(superuser, existing_user)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertEqual(superuser.email, superuser_data['email'])
        self.assertEqual(superuser.username, superuser_data['username'])

