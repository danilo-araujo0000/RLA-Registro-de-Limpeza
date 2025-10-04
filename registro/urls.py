from django.urls import path
from . import views

urlpatterns = [
    path('', views.redirect_view, name='redirect_view'),
    path('salas/', views.salas_view, name='salas_view'),
    path('sala/<int:sala_id>/', views.index_view, name='index_view'),
    path('registro/<int:sala_id>/', views.registro_view, name='registro_view'),
    path('historico/<int:sala_id>/', views.historico_view, name='historico_view'),
    path('login-relatorio/', views.login_relatorio_view, name='login_relatorio_view'),
    path('relatorio/', views.relatorio_view, name='relatorio_view'),
    path('obter-registro/<int:registro_id>/', views.obter_registro_view, name='obter_registro_view'),
    path('atualizar-registro/<int:registro_id>/', views.atualizar_registro_view, name='atualizar_registro_view'),
    path('excluir-registro/<int:registro_id>/', views.excluir_registro_view, name='excluir_registro_view'),
    path('salvar/', views.salvar_registro_view, name='salvar_registro_view'),
    path('sucesso/', views.sucesso_view, name='sucesso_view'),
]