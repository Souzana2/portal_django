from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.urls import reverse
from .models import validar_nif, Empresa, Formador, Formando, Curso, Acao, Inscricao


class NifValidationTest(TestCase):
    def test_nif_valido(self):
        nifs_validos = ['123456789', '999999990', '111111110']
        for nif in nifs_validos:
            try:
                result = validar_nif(nif)
                self.assertEqual(result, nif)
            except ValidationError:
                self.fail(f'NIF {nif} deveria ser válido')

    def test_nif_invalido_digito_controlo(self):
        with self.assertRaises(ValidationError):
            validar_nif('123456780')

    def test_nif_curto(self):
        with self.assertRaises(ValidationError):
            validar_nif('12345')

    def test_nif_comeca_zero(self):
        with self.assertRaises(ValidationError):
            validar_nif('012345678')

    def test_nif_com_pontuacao(self):
        try:
            result = validar_nif('123.456.789')
            self.assertEqual(result, '123456789')
        except ValidationError:
            self.fail('NIF com pontuação deveria ser limpo e válido')


class EmpresaModelTest(TestCase):
    def setUp(self):
        self.empresa = Empresa(
            nome='Empresa Teste',
            nif='123456789',
            localidade='Lisboa'
        )

    def test_str(self):
        self.assertIn('Empresa Teste', str(self.empresa))
        self.assertIn('123456789', str(self.empresa))


class FormadorModelTest(TestCase):
    def test_str(self):
        formador = Formador(nome='Formador Teste', codigo='FT001')
        self.assertEqual(str(formador), 'Formador Teste')


class FormandoModelTest(TestCase):
    def test_str(self):
        formando = Formando(nome='Formando Teste', nif='999999990')
        self.assertIn('Formando Teste', str(formando))
