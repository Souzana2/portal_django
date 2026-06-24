from django.test import TestCase, Client
from django.contrib.auth.models import User, Permission
from django.urls import reverse


class FormacaoViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='test123')
        view_perm = Permission.objects.get(codename='view_acao')
        self.user.user_permissions.add(view_perm)

    def test_acao_lista_login_required(self):
        response = self.client.get(reverse('formacao:acao_lista'))
        self.assertEqual(response.status_code, 302)

    def test_inscricao_lista_login_required(self):
        response = self.client.get(reverse('formacao:inscricao_lista'))
        self.assertEqual(response.status_code, 302)

    def test_acao_lista_authenticated(self):
        self.client.login(username='test', password='test123')
        response = self.client.get(reverse('formacao:acao_lista'))
        self.assertEqual(response.status_code, 200)

    def test_acao_lista_sem_permissao(self):
        user2 = User.objects.create_user(username='test2', password='test123')
        self.client.login(username='test2', password='test123')
        response = self.client.get(reverse('formacao:acao_lista'))
        self.assertEqual(response.status_code, 403)
