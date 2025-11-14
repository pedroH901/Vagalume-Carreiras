# apps/usuarios/permissions.py
from rest_framework import permissions

# 1. Permissão para Usuários Administradores
class IsAdministrador(permissions.BasePermission):
    """
    Permite acesso apenas se o usuário for um superusuário 
    OU tiver o tipo_usuario 'administrador'.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser:
            return True
            
        # CORREÇÃO: Checa o campo 'tipo_usuario'
        # (Assumindo que você tenha um tipo 'administrador', se não, ajuste)
        return request.user.tipo_usuario == 'administrador'

# 2. Permissão para Perfis de Recrutador
class IsRecrutador(permissions.BasePermission):
    """
    Permite acesso apenas se o usuário tiver o tipo_usuario 'recrutador'.
    """
    def has_permission(self, request, view):
        # CORREÇÃO: Checa o campo 'tipo_usuario'
        return request.user.is_authenticated and request.user.tipo_usuario == 'recrutador'

# 3. Permissão para Perfis de Candidato
class IsCandidato(permissions.BasePermission):
    """
    Permite acesso apenas se o usuário tiver o tipo_usuario 'candidato'.
    """
    def has_permission(self, request, view):
        # CORREÇÃO: Checa o campo 'tipo_usuario'
        return request.user.is_authenticated and request.user.tipo_usuario == 'candidato'