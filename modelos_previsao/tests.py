from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse


class ModelosPrevisaoViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='test123')

    def test_radar_risco_login_required(self):
        response = self.client.get(reverse('modelos_previsao:radar_risco'))
        self.assertEqual(response.status_code, 302)

    def test_auditoria_login_required(self):
        response = self.client.get(reverse('modelos_previsao:auditoria_encerramento'))
        self.assertEqual(response.status_code, 302)
