from django.db import models


class IPPermitido(models.Model):
    ip_address = models.GenericIPAddressField(
        unique=True,
        verbose_name='Endereço IP',
        help_text='Endereço IP permitido para acessar o sistema'
    )
    descricao = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Descrição',
        help_text='Descrição do dispositivo/local (ex: Tablet Sala 1)'
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name='Ativo',
        help_text='IP está ativo e permitido'
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )

    class Meta:
        verbose_name = 'IP Permitido'
        verbose_name_plural = 'IPs Permitidos'
        ordering = ['-ativo', 'ip_address']

    def __str__(self):
        status = "✓" if self.ativo else "✗"
        if self.descricao:
            return f"{status} {self.ip_address} - {self.descricao}"
        return f"{status} {self.ip_address}"


class DispositivoPermitido(models.Model):
    identificador = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='ID do Dispositivo',
        help_text='Identificador configurado no aplicativo'
    )
    descricao = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Descricao',
        help_text='Descricao do dispositivo/local (ex: Tablet Sala 1B)'
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name='Ativo',
        help_text='Dispositivo esta autorizado'
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criacao'
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name='Ultima Atualizacao'
    )

    class Meta:
        verbose_name = 'Dispositivo Permitido'
        verbose_name_plural = 'Dispositivos Permitidos'
        ordering = ['-ativo', 'identificador']

    def __str__(self):
        status = "V" if self.ativo else "?"
        if self.descricao:
            return f"{status} {self.identificador} - {self.descricao}"
        return f"{status} {self.identificador}"


class UserRelatorio(models.Model):
    username = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Usuário'
    )
    password = models.CharField(
        max_length=255,
        verbose_name='Senha'
    )
    edit = models.BooleanField(
        default=False,
        verbose_name='Permissão de Edição',
        help_text='Se ativo, o usuário NÃO pode acessar a view de edição'
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )

    class Meta:
        verbose_name = 'Usuário de Relatório'
        verbose_name_plural = 'Usuários de Relatório'
        ordering = ['username']
        db_table = 'users_relatorio'

    def __str__(self):
        return f"{self.username} {'(Bloqueado para edição)' if self.edit else ''}"