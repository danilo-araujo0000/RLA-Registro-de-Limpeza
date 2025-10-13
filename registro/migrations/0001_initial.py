

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IPPermitido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(help_text='Endereço IP permitido para acessar o sistema', unique=True, verbose_name='Endereço IP')),
                ('descricao', models.CharField(blank=True, help_text='Descrição do dispositivo/local (ex: Tablet Sala 1, Computador Recepção)', max_length=200, verbose_name='Descrição')),
                ('ativo', models.BooleanField(default=True, help_text='IP está ativo e permitido', verbose_name='Ativo')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Última Atualização')),
            ],
            options={
                'verbose_name': 'IP Permitido',
                'verbose_name_plural': 'IPs Permitidos',
                'ordering': ['-ativo', 'ip_address'],
            },
        ),
    ]