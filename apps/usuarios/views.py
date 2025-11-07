from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import CandidatoCadastroForm # Importa o formulário que acabamos de criar
from .models import Usuario, Candidato
from django.db import transaction # Garante que os dois models sejam criados com segurança
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .models import Resumo_Profissional

@transaction.atomic # Garante que ou os dois são criados, ou nenhum é
def cadastrar_candidato(request):
    """
    Processa o formulário de cadastro do UC01.
    """
    if request.method == 'POST':
        form = CandidatoCadastroForm(request.POST)
        
        if form.is_valid():
            data = form.cleaned_data
            
            # 1. Cria o Usuario (Portaria) 
            # Usamos o email como username, como discutido
            user = Usuario.objects.create_user(
                username=data['email'], # Usa email como username
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                telefone=data['telefone'],
                tipo_usuario='candidato'
            )
            
            # 2. Cria o Candidato (Sala) 
            candidato = Candidato.objects.create(
                usuario=user, # Conecta o perfil ao login
                cpf=data['cpf']
            )
            
            # 3. Loga o usuário automaticamente após o cadastro
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            messages.info(request, 'Bem-vindo!', extra_tags='FIRST_LOGIN')
            
            # Redireciona para o painel do candidato (vamos criar essa URL depois)
            return redirect('onboarding_bem_vindo')
    
    else:
        # Se for um GET (usuário só abriu a página), mostra um form vazio [cite: 11]
        form = CandidatoCadastroForm()
        
    # Renderiza a página HTML, passando o formulário para ela
    return render(request, 'usuarios/cadastro_candidato.html', {'form': form})

def login_view(request):
    """
    Processa a página de login para Candidatos e Recrutadores (UC03).
    """
    if request.method == 'POST':
        # No HTML, o <input> deve ter name="username"
        login_identifier = request.POST.get('username')
        password = request.POST.get('password')

        # O 'authenticate' agora usa nosso EmailOrCPFBackend
        user = authenticate(request, username=login_identifier, password=password)

        if user is not None:
            # Detecta se é o primeiro login
            is_first_login = (user.last_login is None)

            # Loga o usuário (isso atualiza o last_login)
            login(request, user)

            # Envia a "flag" se for o primeiro login de um candidato
            if is_first_login and user.tipo_usuario == 'candidato':
                messages.info(request, 'Bem-vindo!', extra_tags='FIRST_LOGIN')
            
            
            # --- TAREFA: CONTROLE DE PERMISSÕES ---
            # Aqui checamos o "crachá" (tipo_usuario)
            if user.tipo_usuario == 'candidato':
                if is_first_login:
                    return redirect('onboarding_bem_vindo')
                else:
                    return redirect('home_candidato')
            elif user.tipo_usuario == 'recrutador':
                return redirect('home_recrutador') # Redireciona para o painel da empresa
            
            return redirect('pagina_padrao') # Uma página genérica
        else:
            # Login falhou, conforme UC03
            messages.error(request, 'Credenciais inválidas. Por favor, tente novamente.')
            
    # Se for um GET ou se o login falhar, mostra a página de login
    return render(request, 'usuarios/login.html')

def logout_view(request):
    """
    Faz o logout do usuário e o redireciona para a tela de login.
    """
    logout(request)
    return redirect('login') # Redireciona para a URL da página de login

@login_required
def onboarding_bem_vindo(request):
    """
    Mostra a Página 1 (Passo 1) da "cutscene" de onboarding.
    """
    # Apenas renderiza o HTML. O botão "Vamos Começar" vai linkar para 'onboarding_resumo'
    return render(request, 'usuarios/onboarding_bem_vindo.html')


@login_required
def onboarding_resumo(request):
    """
    Mostra e Processa a Página 2 (Resumo Profissional).
    """
    candidato = request.user.candidato

    if request.method == 'POST':
        # Pega o texto do <textarea name="resumo">
        texto_resumo = request.POST.get('resumo', '')
        
        # Salva no banco de dados
        # update_or_create: cria um novo ou atualiza um existente
        Resumo_Profissional.objects.update_or_create(
            candidato=candidato,
            defaults={'texto': texto_resumo}
        )
        
        # Redireciona para o próximo passo
        return redirect('onboarding_experiencia')

    # Se for um GET, apenas mostra a página
    return render(request, 'usuarios/onboarding_resumo.html')


@login_required
def onboarding_experiencia(request):
    """
    Mostra a Página 3 (Experiências), como você pediu.
    """
    # Esta é a sua próxima página
    return HttpResponse("<h1>Experiências Profissionais</h1><p>Liste seus empregos anteriores e suas responsabilidades.</p>")

@login_required
def salvar_resumo(request):
    """
    Esta view recebe o POST do formulário de resumo (Bloco 2)
    e o salva no banco de dados.
    """
    if request.method == 'POST':
        # 1. Pega o texto do <textarea name="resumo">
        texto_resumo = request.POST.get('resumo', '')

        try:
            # 2. Pega o perfil 'Candidato' do usuário que está logado
            candidato = request.user.candidato

            # 3. Salva no banco de dados
            # update_or_create: cria um novo ou atualiza um existente
            Resumo_Profissional.objects.update_or_create(
                candidato=candidato,
                defaults={'texto': texto_resumo}
            )

            messages.success(request, 'Resumo salvo com sucesso!')

            # 4. Redireciona para o próximo passo (Experiência)
            # (Vamos criar essa URL 'onboarding_experiencia' em seguida)
            return redirect('onboarding_experiencia') 

        except Candidato.DoesNotExist:
            messages.error(request, 'Erro: Perfil de candidato não encontrado.')
            return redirect('home_candidato')

    # Se alguém tentar acessar a URL via GET, apenas redireciona
    return redirect('home_candidato')