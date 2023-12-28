from django.test import TestCase
from srcs_auth import services
import requests
from mock import patch, Mock
import json

class TestAuthServices(TestCase):

    @patch.object(services, 'requests', Mock(wraps=requests))
    def test_exchange_code_on_success(self):
        services.requests.post.return_value = Mock(spec=requests.Response, json=Mock(return_value=json.load('{"access_token": "cavalinho"}')))
        services.requests.get.return_value = Mock(spec=requests.Response, json=Mock(return_value=json.load('{"user": "cavalinho"}')))
        
        result = services.exchange_code('cavalinho')

        self.assertEqual(result['user'], 'cavalinho')
