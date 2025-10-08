from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registro', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DispositivoPermitido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identificador', models.CharField(help_text='Identificador configurado no aplicativo', max_length=100, unique=True, verbose_name='ID do Dispositivo')),
                ('descricao', models.CharField(blank=True, help_text='Descricao do dispositivo/local (ex: Tablet Sala 1, Smartphone Setor B)', max_length=200, verbose_name='Descricao')),
                ('ativo', models.BooleanField(default=True, help_text='Dispositivo esta autorizado', verbose_name='Ativo')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de Criacao')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Ultima Atualizacao')),
            ],
            options={
                'ordering': ['-ativo', 'identificador'],
                'verbose_name': 'Dispositivo Permitido',
                'verbose_name_plural': 'Dispositivos Permitidos',
            },
        ),
    ]
