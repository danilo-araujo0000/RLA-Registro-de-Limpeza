from django.contrib import admin
from .models import IPPermitido, DispositivoPermitido, UserRelatorio


@admin.register(IPPermitido)
class IPPermitidoAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'descricao', 'ativo', 'data_criacao', 'data_atualizacao')
    list_filter = ('ativo', 'data_criacao')
    search_fields = ('ip_address', 'descricao')
    list_editable = ('ativo',)
    readonly_fields = ('data_criacao', 'data_atualizacao')

    fieldsets = (
        ('Informações do IP', {
            'fields': ('ip_address', 'descricao', 'ativo')
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DispositivoPermitido)
class DispositivoPermitidoAdmin(admin.ModelAdmin):
    list_display = ('identificador', 'descricao', 'ativo', 'data_criacao', 'data_atualizacao')
    list_filter = ('ativo', 'data_criacao')
    search_fields = ('identificador', 'descricao')
    list_editable = ('ativo',)
    readonly_fields = ('data_criacao', 'data_atualizacao')

    fieldsets = (
        ('Informaes do Dispositivo', {
            'fields': ('identificador', 'descricao', 'ativo')
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserRelatorio)
class UserRelatorioAdmin(admin.ModelAdmin):
    list_display = ('username', 'edit', 'ativo', 'data_criacao')
    list_filter = ('ativo', 'edit', 'data_criacao')
    search_fields = ('username',)
    list_editable = ('ativo', 'edit')
    readonly_fields = ('data_criacao',)

    fieldsets = (
        ('Credenciais', {
            'fields': ('username', 'password')
        }),
        ('Permissões', {
            'fields': ('edit', 'ativo')
        }),
        ('Datas', {
            'fields': ('data_criacao',),
            'classes': ('collapse',)
        }),
    )