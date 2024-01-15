from django.test import TestCase
from srcs_auth import services
import requests
from mock import patch, Mock
import json
import django.http as http

class TestAuthServices(TestCase):

    @patch.object(services, 'requests', Mock(wraps=requests))
    def test_exchange_code_on_success(self):
        services.requests.post.return_value = Mock(
            spec=requests.Response,
            status_code=200,
            ok=True,
            json=Mock(return_value=json.loads('{"access_token": "cavalinho"}'))
        )
        services.requests.get.return_value = Mock(
            spec=requests.Response,
            status_code=200,
            ok=True,
            json=Mock(return_value=json.loads('{"user": "cavalinho"}'))
        )
        
        result = services.exchange_code('cavalinho')

        self.assertEqual(result['user'], 'cavalinho')

    @patch.object(services, 'requests', Mock(wraps=requests))
    def test_exchange_code_on_fail_at_token_post(self):
        services.requests.post.return_value = Mock(
            spec=requests.Response,
            status_code=401,
            ok=False,
            json=Mock(return_value=json.loads('{}'))
        )
        
        self.assertRaises(ValueError, services.exchange_code, 'cavalinho')

    @patch.object(services, 'requests', Mock(wraps=requests))
    def test_exchange_code_on_fail_at_user_get(self):
        services.requests.post.return_value = Mock(
            spec=requests.Response,
            status_code=200,
            ok=True,
            json=Mock(return_value=json.loads('{"access_token": "cavalinho"}'))
        )

        services.requests.get.return_value = Mock(
            spec=requests.Response,
            status_code=401,
            ok=False,
            json=Mock(return_value=json.loads('{}'))
        )

        self.assertRaises(Exception, services.exchange_code, 'cavalinho')

