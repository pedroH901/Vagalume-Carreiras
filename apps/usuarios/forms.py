from django import forms
from .models import Usuario, Candidato
import re # Para limpar o CPF

class CandidatoCadastroForm(forms.Form):
    """
    Formulário para o fluxo UC01: Cadastrar Novo Candidato.
    Coleta dados para os models Usuario e Candidato.
    """
    
    first_name = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Nome'}))
    last_name = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Sobrenome'}))
    email = forms.EmailField(label='', widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    telefone = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Telefone'}))
    cpf = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'CPF'}))
    password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Senha'}))
    password_confirm = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar Senha'}))

def clean_cpf(self):
        # Validação do CPF 
        cpf = self.cleaned_data.get('cpf')
        cpf_digits = re.sub(r'[^0-9]', '', cpf) # Remove pontos e traços
        
        if len(cpf_digits) != 11:
            raise forms.ValidationError("CPF deve conter 11 dígitos.")
        
        # Validação de unicidade
        if Candidato.objects.filter(cpf=cpf_digits).exists():
            raise forms.ValidationError("Este CPF já está cadastrado. Tente fazer login.")
        
        return cpf_digits # Retorna o CPF limpo

def clean_email(self):
        # Validação de unicidade do Email
        email = self.cleaned_data.get('email').lower()
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email já está cadastrado. Tente fazer login.") 
        return email

def clean(self):
        # Validação para checar se as senhas coincidem
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("As senhas não coincidem.")
        
        return cleaned_data

def clean_telefone(self):
    # Validação de unicidade do Telefone
    telefone = self.cleaned_data.get('telefone')
    # (Opcional: limpar o telefone de máscaras, similar ao CPF)
    # telefone_digits = re.sub(r'[^0-9]', '', telefone) 

    if Usuario.objects.filter(telefone=telefone).exists():
        raise forms.ValidationError("Este telefone já está cadastrado.")
    return telefone