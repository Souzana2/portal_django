from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entidades', '0010_criar_grupos'),
    ]

    MODELS = [
        'acao', 'curso', 'empresa', 'formador', 'formando', 'inscricao',
        'historicalacao', 'historicalcurso', 'historicalempresa',
        'historicalformador', 'historicalformando', 'historicalinscricao',
    ]

    operations = [
        migrations.AlterField(
            model_name=model_name,
            name='created_at',
            field=models.DateTimeField(blank=True, null=True),
        )
        for model_name in MODELS
    ] + [
        migrations.AlterField(
            model_name=model_name,
            name='updated_at',
            field=models.DateTimeField(blank=True, null=True),
        )
        for model_name in MODELS
    ]
