"""Formulários com validação de NIF e campos crispy."""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field
from .models import Empresa, Formador, Formando, Acao, Inscricao, Curso


class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nome', 'nif', 'morada', 'codigo_postal', 'localidade']
        widgets = {'morada': forms.Textarea(attrs={'rows': 2})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('nome', css_class='col-md-8'), Column('nif', css_class='col-md-4')),
            'morada',
            Row(Column('codigo_postal', css_class='col-md-3'), Column('localidade', css_class='col-md-9')),
            Submit('submit', 'Guardar', css_class='btn btn-primary'),
        )

    def clean_nif(self):
        nif = self.cleaned_data.get('nif')
        if nif:
            qs = Empresa.objects.filter(nif=nif)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Já existe uma empresa ativa com este NIF.')
        return nif


class FormadorForm(forms.ModelForm):
    class Meta:
        model = Formador
        fields = ['nome', 'codigo', 'data_nascimento', 'morada', 'codigo_postal',
                  'descricao_postal', 'telefone1', 'telefone2', 'email1', 'email2']
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'morada': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('nome', css_class='col-md-8'), Column('codigo', css_class='col-md-4')),
            'morada',
            Row(Column('codigo_postal', css_class='col-md-3'), Column('descricao_postal', css_class='col-md-9')),
            Row(Column('telefone1', css_class='col-md-6'), Column('telefone2', css_class='col-md-6')),
            Row(Column('email1', css_class='col-md-6'), Column('email2', css_class='col-md-6')),
            'data_nascimento',
            Submit('submit', 'Guardar', css_class='btn btn-primary'),
        )

    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if nome:
            qs = Formador.objects.filter(nome=nome)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Já existe um formador ativo com este nome.')
        return nome


class FormandoForm(forms.ModelForm):
    class Meta:
        model = Formando
        fields = ['nome', 'nif', 'tipo_identificacao', 'numero_identificacao',
                  'validade_identificacao', 'naturalidade', 'data_nascimento',
                  'morada', 'codigo_postal', 'localidade', 'telefone', 'email', 'empresa']
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'validade_identificacao': forms.DateInput(attrs={'type': 'date'}),
            'morada': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('nome', css_class='col-md-8'), Column('nif', css_class='col-md-4')),
            Row(Column('tipo_identificacao', css_class='col-md-4'),
                Column('numero_identificacao', css_class='col-md-4'),
                Column('validade_identificacao', css_class='col-md-4')),
            Row(Column('data_nascimento', css_class='col-md-4'),
                Column('naturalidade', css_class='col-md-8')),
            'morada',
            Row(Column('codigo_postal', css_class='col-md-3'), Column('localidade', css_class='col-md-9')),
            Row(Column('telefone', css_class='col-md-4'), Column('email', css_class='col-md-8')),
            'empresa',
            Submit('submit', 'Guardar', css_class='btn btn-primary'),
        )

    def clean_nif(self):
        nif = self.cleaned_data.get('nif')
        if nif:
            qs = Formando.objects.filter(nif=nif)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Já existe um formando ativo com este NIF.')
        return nif


class InscricaoForm(forms.ModelForm):
    class Meta:
        model = Inscricao
        fields = ['formando', 'acao', 'empresa', 'data_inscricao',
                  'estado_profissional', 'data_estado_profissional',
                  'numero_certificado', 'estado_pagamento', 'comercial']
        widgets = {
            'data_inscricao': forms.DateInput(attrs={'type': 'date'}),
            'data_estado_profissional': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('formando', css_class='col-md-6'), Column('acao', css_class='col-md-6')),
            Row(Column('empresa', css_class='col-md-6'), Column('data_inscricao', css_class='col-md-6')),
            Row(Column('estado_profissional', css_class='col-md-4'),
                Column('data_estado_profissional', css_class='col-md-4'),
                Column('numero_certificado', css_class='col-md-4')),
            Row(Column('estado_pagamento', css_class='col-md-4'), Column('comercial', css_class='col-md-8')),
            Submit('submit', 'Guardar', css_class='btn btn-primary'),
        )

    def clean(self):
        cleaned_data = super().clean()
        formando = cleaned_data.get('formando')
        acao = cleaned_data.get('acao')
        if formando and acao:
            qs = Inscricao.objects.filter(formando=formando, acao=acao)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Este formando já está inscrito nesta ação.')
        return cleaned_data


class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['codigo', 'nome', 'area_codigo', 'area_nome']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('codigo', css_class='col-md-4'), Column('nome', css_class='col-md-8')),
            Row(Column('area_codigo', css_class='col-md-4'), Column('area_nome', css_class='col-md-8')),
            Submit('submit', 'Guardar', css_class='btn btn-primary'),
        )

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if codigo:
            qs = Curso.objects.filter(codigo=codigo)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Já existe um curso ativo com este código.')
        return codigo
