from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class CoreViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='test123')

    def test_dashboard_login_required(self):
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_authenticated(self):
        self.client.login(username='test', password='test123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_pesquisa_login_required(self):
        response = self.client.get(reverse('core:pesquisa'))
        self.assertEqual(response.status_code, 302)
