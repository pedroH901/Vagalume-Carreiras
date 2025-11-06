# Arquivo: apps/vagas/urls.py

from django.urls import path
from . import views  # Importa as views do app (views.py)

urlpatterns = [
    path('vagas/criar/', views.criar_vaga, name='criar_vaga'),
    path('vagas/editar/<int:vaga_id>/', views.editar_vaga, name='editar_vaga'),
    path('vagas/deletar/<int:vaga_id>/', views.deletar_vaga, name='deletar_vaga'),
    path('vagas/aplicar/<int:vaga_id>/', views.aplicar_vaga, name='aplicar_vaga'),
    path('dashboard/candidato/', views.home_candidato, name='home_candidato'),
    path('dashboard/recrutador/', views.home_recrutador, name='home_recrutador'),
]