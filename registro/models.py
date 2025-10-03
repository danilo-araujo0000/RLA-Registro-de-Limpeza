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
    tipo_limpeza = models.CharField(max_length=20)
    obs = models.CharField(max_length=1000, blank=True, null=True)
    portas = models.CharField(max_length=2, blank=True, null=True)
    teto = models.CharField(max_length=2, blank=True, null=True)
    paredes = models.CharField(max_length=2, blank=True, null=True)
    janelas = models.CharField(max_length=2, blank=True, null=True)
    piso = models.CharField(max_length=2, blank=True, null=True)
    superficie_mobiliario = models.CharField(max_length=2, blank=True, null=True)
    dispenser = models.CharField(max_length=2, blank=True, null=True)
    criticidade = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'if_tbl_registro_higiene'