from django.db import models

class Setor(models.Model):
    id_setor = models.AutoField(primary_key=True)
    nome_setor = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'if_tbl_setores_higiene'

class Sala(models.Model):
    id_sala = models.AutoField(primary_key=True)
    setor = models.ForeignKey(Setor, on_delete=models.DO_NOTHING, db_column='id_setor')
    nome_sala = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'if_tbl_sala_higiene'

class RegistroHigiene(models.Model):
    id_registro = models.AutoField(primary_key=True)
    sala = models.ForeignKey(Sala, on_delete=models.DO_NOTHING, db_column='id_sala')
    colaborador = models.CharField(max_length=255)
    data_limpeza = models.DateField()
    hora_limpeza = models.CharField(max_length=5)
    id_tipo_limpeza = models.IntegerField()
    obs = models.CharField(max_length=1000, blank=True, null=True)
    portas = models.CharField(max_length=2, blank=True, null=True)
    teto = models.CharField(max_length=2, blank=True, null=True)
    paredes = models.CharField(max_length=2, blank=True, null=True)
    janelas = models.CharField(max_length=2, blank=True, null=True)
    piso = models.CharField(max_length=2, blank=True, null=True)
    superficie_mobiliario = models.CharField(max_length=2, blank=True, null=True)
    dispenser = models.CharField(max_length=2, blank=True, null=True)
    id_criticidade = models.IntegerField(blank=True, null=True)
    papel_hig = models.CharField(max_length=2, blank=True, null=True)
    papel_toalha = models.CharField(max_length=2, blank=True, null=True)
    alcool = models.CharField(max_length=2, blank=True, null=True)
    sabonete = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'if_tbl_registro_higiene'


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
        help_text='Descrição do dispositivo/local (ex: Tablet Sala 1, Computador Recepção)'
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
        help_text='Descricao do dispositivo/local (ex: Tablet Sala 1, Smartphone Setor B)'
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
