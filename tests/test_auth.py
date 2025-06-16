from django.test import TestCase
from rest_framework.test import APIClient

class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_signup(self):
        response = self.client.post('/api/resume/auth/signup/', {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('tokens', response.data)

    def test_signin(self):
        self.client.post('/api/resume/auth/signup/', {
            'username': 'testuser2',
            'email': 'test2@example.com',
            'password': 'testpass123'
        })
        response = self.client.post('/api/resume/auth/signin/', {
            'email': 'test2@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('tokens', response.data)
