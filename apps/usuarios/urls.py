# Arquivo: apps/usuarios/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # URLs de autenticação (permanecem iguais)
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cadastro/candidato/', views.cadastrar_candidato, name='cadastro_candidato'),

    # ATENÇÃO: Removemos as URLs de /onboarding/ aqui
    
    # --- NOVAS URLs (Endpoints de AJAX) ---
    path('ajax/salvar-resumo/', views.ajax_salvar_resumo, name='ajax_salvar_resumo'),
    path('ajax/salvar-experiencia/', views.ajax_salvar_experiencia, name='ajax_salvar_experiencia'),
    path('ajax/salvar-formacao/', views.ajax_salvar_formacao, name='ajax_salvar_formacao'),
]