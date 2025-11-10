# Arquivo: apps/usuarios/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.db import transaction
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError

# 1. IMPORTE OS MODELS E FORMS QUE CRIAMOS
from .models import (
    Usuario, Candidato, Resumo_Profissional, 
    Experiencia, Formacao_Academica, Skill
)
from .forms import (
    CandidatoCadastroForm, ExperienciaForm, 
    FormacaoForm, SkillForm, CurriculoForm
)


@transaction.atomic
def cadastrar_candidato(request):
    """
    Processa o formulário de cadastro do UC01.
    """
    if request.method == 'POST':
        form = CandidatoCadastroForm(request.POST)
        
        if form.is_valid():
            # ... (seu código de criação do user e candidato continua igual) ...
            data = form.cleaned_data
            
            user = Usuario.objects.create_user(
                username=data['email'],
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                telefone=data['telefone'],
                tipo_usuario='candidato'
            )
            
            candidato = Candidato.objects.create(
                usuario=user,
                cpf=data['cpf']
            )
            
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.info(request, 'Bem-vindo!', extra_tags='FIRST_LOGIN')
            
            # --- CORREÇÃO IMPORTANTE ---
            # Redireciona para o INÍCIO da "cutscene", não para o final.
            return redirect('home_candidato') 
            # ---------------------------
    
    else:
        form = CandidatoCadastroForm()
        
    return render(request, 'usuarios/cadastro_candidato.html', {'form': form})

def login_view(request):
    """
    Processa a página de login para Candidatos e Recrutadores (UC03).
    """
    if request.method == 'POST':
        login_identifier = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=login_identifier, password=password)

        if user is not None:
            is_first_login = (user.last_login is None)
            login(request, user)

            if user.tipo_usuario == 'candidato':
                if is_first_login:
                    # Inicia a "cutscene"
                    return redirect('onboarding_bem_vindo') 
                else:
                    # Vai direto para o painel
                    return redirect('home_candidato')
            elif user.tipo_usuario == 'recrutador':
                return redirect('home_recrutador')
            
            return redirect('home_candidato')
        else:
            messages.error(request, 'Credenciais inválidas. Por favor, tente novamente.')
            
    return render(request, 'usuarios/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# ---
# AQUI COMEÇA A "CUTSCENE" DE ONBOARDING
# ---







@login_required
def onboarding_formacao(request):
    """
    Passo 4: Adiciona Formação Acadêmica (70% progresso).
    """
    candidato = request.user.candidato
    progresso = 70

    if request.method == 'POST':
        form = FormacaoForm(request.POST)
        if form.is_valid():
            formacao = form.save(commit=False)
            formacao.candidato = candidato
            formacao.save()
            
            if 'continuar' in request.POST:
                return redirect('onboarding_skills') # Próximo passo
            else:
                return redirect('onboarding_formacao')
    else:
        form = FormacaoForm()

    formacoes_salvas = Formacao_Academica.objects.filter(candidato=candidato).order_by('-data_inicio')
    
    return render(request, 'usuarios/onboarding_formacao.html', {
        'form': form,
        'formacoes': formacoes_salvas,
        'progress': progresso
    })

@login_required
def onboarding_skills(request):
    """
    Passo 5: Adiciona Skills (85% progresso).
    """
    candidato = request.user.candidato
    progresso = 85

    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.candidato = candidato
            skill.save()
            
            if 'continuar' in request.POST:
                return redirect('onboarding_curriculo') # Próximo passo
            else:
                return redirect('onboarding_skills')
    else:
        form = SkillForm()

    skills_salvas = Skill.objects.filter(candidato=candidato)
    
    return render(request, 'usuarios/onboarding_skills.html', {
        'form': form,
        'skills': skills_salvas,
        'progress': progresso
    })

@login_required
def onboarding_curriculo(request):
    """
    Passo 6: Upload do Currículo PDF (100% progresso).
    """
    candidato = request.user.candidato
    progresso = 100

    if request.method == 'POST':
        # IMPORTANTE: request.FILES é necessário para uploads
        form = CurriculoForm(request.POST, request.FILES, instance=candidato)
        if form.is_valid():
            form.save()
            # Fim da "cutscene"! Redireciona para o painel principal.
            return redirect('home_candidato')
    else:
        form = CurriculoForm(instance=candidato)

    return render(request, 'usuarios/onboarding_curriculo.html', {
        'form': form,
        'progress': progresso
    })

@login_required
def ajax_salvar_resumo(request):
    if request.method == 'POST':
        candidato = request.user.candidato
        texto_resumo = request.POST.get('resumo', '')
        
        Resumo_Profissional.objects.update_or_create(
            candidato=candidato,
            defaults={'texto': texto_resumo}
        )
        
        # Responde com JSON para o JavaScript
        return JsonResponse({
            'status': 'success',
            'action': 'next_step' # Diz ao JS para avançar
        })
    return JsonResponse({'status': 'error', 'message': 'Método GET não permitido'})

@login_required
def ajax_salvar_experiencia(request):
    if request.method == 'POST':
        form = ExperienciaForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.candidato = request.user.candidato
            exp.save()
            
            # Checa qual botão o JS enviou
            if 'continuar' in request.POST:
                return JsonResponse({
                    'status': 'success',
                    'action': 'next_step'
                })
            else:
                # "Salvar e Adicionar Outro"
                return JsonResponse({
                    'status': 'success',
                    'action': 'add_another',
                    'list_id': 'lista-experiencias',
                    # Envia um mini-HTML para o JS adicionar na lista
                    'saved_item_html': f'<p><strong>{exp.cargo}</strong> em {exp.empresa}</p>' 
                })
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors.as_json()})
    return JsonResponse({'status': 'error', 'message': 'Método GET não permitido'})

@login_required
def ajax_salvar_formacao(request):
    if request.method == 'POST':
        form = FormacaoForm(request.POST)
        if form.is_valid():
            formacao = form.save(commit=False)
            formacao.candidato = request.user.candidato
            formacao.save()
            
            if 'continuar' in request.POST:
                return JsonResponse({'status': 'success', 'action': 'next_step'})
            else:
                return JsonResponse({
                    'status': 'success',
                    'action': 'add_another',
                    'list_id': 'lista-formacoes',
                    'saved_item_html': f'<p><strong>{formacao.nome_formacao}</strong> em {formacao.nome_instituicao}</p>'
                })
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors.as_json()})
    return JsonResponse({'status': 'error', 'message': 'Método GET não permitido'})

@login_required
def ajax_salvar_skill(request):
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.candidato = request.user.candidato
            skill.save()

            if 'continuar' in request.POST:
                return JsonResponse({'status': 'success', 'action': 'next_step'})
            else: # "Salvar e Adicionar Outro"
                return JsonResponse({
                    'status': 'success',
                    'action': 'add_another',
                    'list_id': 'lista-skills',
                    # get_tipo_display pega o "Hard Skill" em vez de "hard"
                    'saved_item_html': f'<p><strong>{skill.nome}</strong> ({skill.get_tipo_display()})</p>'
                })
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors.as_json()})
    return JsonResponse({'status': 'error', 'message': 'Método GET não permitido'})

@login_required
def ajax_salvar_curriculo(request):
    if request.method == 'POST':
        candidato = request.user.candidato
        # IMPORTANTE: Usamos request.FILES para arquivos
        form = CurriculoForm(request.POST, request.FILES, instance=candidato) 

        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'action': 'next_step'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors.as_json()})
    return JsonResponse({'status': 'error', 'message': 'Método GET não permitido'})