from django.contrib import admin
from .models import IPPermitido, DispositivoPermitido


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
        ('Informa��es do Dispositivo', {
            'fields': ('identificador', 'descricao', 'ativo')
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
