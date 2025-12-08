from django.core.management.base import BaseCommand
from apps.usuarios.models import Usuario, Candidato, Empresa, Recrutador, Skill, Experiencia, Resumo_Profissional
from apps.vagas.models import Vaga, Plano
import datetime
import random

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados massivos de teste'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Iniciando Seed Robusto...')

        # 1. PLANOS
        planos = [
            {'chave': 'basico', 'nome': 'Básico', 'preco': 0.00, 'limite': 1},
            {'chave': 'intermediario', 'nome': 'Intermediário', 'preco': 150.00, 'limite': 10},
            {'chave': 'premium', 'nome': 'Premium', 'preco': 400.00, 'limite': 999},
        ]
        for p in planos:
            Plano.objects.get_or_create(nome_chave=p['chave'], defaults={'nome_exibicao': p['nome'], 'preco': p['preco'], 'limite_vagas': p['limite']})

        # 2. ADMIN
        if not Usuario.objects.filter(email='admin@vagalume.com').exists():
            Usuario.objects.create_superuser('admin@vagalume.com', 'admin@vagalume.com', 'admin', first_name='Super', last_name='Admin')

 # 3. EMPRESAS E RECRUTADORES (3 Empresas diferentes)
 # 3. EMPRESAS, RECRUTADORES E VAGAS MASSIVAS
        self.stdout.write('🏭 Gerando Empresas e Vagas...')
        
        empresas_data = [
            {'nome': 'Vagalume Tech', 'setor': 'Tecnologia', 'cnpj': '10000000000100', 'rec_nome': 'Chefe', 'rec_email': 'recrutador@vagalume.com'},
            {'nome': 'InovaSoft', 'setor': 'Tecnologia', 'cnpj': '20000000000100', 'rec_nome': 'Ana', 'rec_email': 'ana@inovasoft.com'},
            {'nome': 'Banco Futuro', 'setor': 'Financeiro', 'cnpj': '30000000000100', 'rec_nome': 'Carlos', 'rec_email': 'carlos@bancofuturo.com'},
            {'nome': 'Agência Criativa', 'setor': 'Marketing', 'cnpj': '40000000000100', 'rec_nome': 'Mariana', 'rec_email': 'mariana@criativa.com'},
            {'nome': 'Global RH', 'setor': 'Recursos Humanos', 'cnpj': '50000000000100', 'rec_nome': 'Roberto', 'rec_email': 'roberto@globalrh.com'},
        ]

        # Lista de áreas para garantir que TODAS tenham vagas
        areas_alvo = [
            'Tecnologia', 'Design', 'Financeiro', 'Marketing', 
            'Recursos Humanos', 'Vendas', 'Jurídico', 'Administração'
        ]
        
        tipos_contrato = ['CLT', 'PJ', 'Remoto', 'Híbrido']

        for emp in empresas_data:
            # Criar ou pegar Empresa
            empresa, created = Empresa.objects.get_or_create(
                cnpj=emp['cnpj'], 
                defaults={
                    'nome': emp['nome'], 
                    'setor': emp['setor'], 
                    'telefone': '11999999999', 
                    'plano_assinado': 'premium' # Premium para não ter limite de vagas
                }
            )
            
            # Criar ou pegar Recrutador
            if not Usuario.objects.filter(email=emp['rec_email']).exists():
                u = Usuario.objects.create_user(
                    emp['rec_email'], emp['rec_email'], '123', 
                    first_name=emp['rec_nome'], last_name='Recrutador', 
                    tipo_usuario='recrutador'
                )
                recrutador = Recrutador.objects.create(usuario=u, empresa=empresa)
            else:
                u = Usuario.objects.get(email=emp['rec_email'])
                # Garante que o usuário existente tenha um perfil de recrutador
                if hasattr(u, 'recrutador'):
                    recrutador = u.recrutador
                else:
                    recrutador = Recrutador.objects.create(usuario=u, empresa=empresa)

            # --- A MÁGICA ACONTECE AQUI: LOOP DE VAGAS ---
            # Para CADA empresa, vamos criar 2 vagas em CADA área
            for area in areas_alvo:
                for i in range(1, 3): # Cria 2 vagas por área (range 1 a 3 exclusive)
                    
                    titulo_vaga = f"{area} Pleno - {emp['nome']}"
                    if i == 2: titulo_vaga = f"Estágio em {area}"
                    
                    salario = random.randint(2, 15) * 1000
                    contrato = random.choice(tipos_contrato)

                    Vaga.objects.create(
                        empresa=empresa, 
                        recrutador=recrutador, 
                        titulo=titulo_vaga,
                        area_atuacao=area, # Essencial para seus filtros funcionarem
                        descricao=f'Estamos buscando profissionais apaixonados por {area} para compor o time da {emp["nome"]}.', 
                        requisitos='Experiência na área, vontade de aprender e proatividade.',
                        tipo_contrato=contrato, 
                        localidade=random.choice(['São Paulo', 'Rio de Janeiro', 'Remoto', 'Curitiba']), 
                        faixa_salarial=f'R$ {salario},00', 
                        status=True,
                        data_publicacao=datetime.datetime.now()
                    )
        
        self.stdout.write(f'✅ Vagas criadas! Total: {len(empresas_data) * len(areas_alvo) * 2} novas vagas.')

        # 4. CANDIDATOS (15 Perfis Variados)
        candidatos_data = [
            # NOME, HEADLINE, SKILLS (Hard), NIVEL
            ('João Python', 'Dev Python Junior', ['Python', 'Django', 'SQL'], 'Iniciante'),
            ('Maria Java', 'Engenheira de Software', ['Java', 'Spring', 'Docker'], 'Pleno'),
            ('Pedro Frontend', 'Dev React', ['JavaScript', 'React', 'CSS'], 'Júnior'),
            ('Lucas Dados', 'Cientista de Dados', ['Python', 'Pandas', 'Machine Learning'], 'Sênior'),
            ('Ana Design', 'UX/UI Designer', ['Figma', 'Adobe XD', 'Prototipagem'], 'Pleno'),
            ('Carla Tech', 'Dev Full Stack', ['Python', 'React', 'Node.js'], 'Sênior'),
            ('Marcos Ops', 'DevOps Engineer', ['AWS', 'Docker', 'Kubernetes'], 'Pleno'),
            ('Julia Mobile', 'Dev iOS', ['Swift', 'iOS', 'Xcode'], 'Júnior'),
            ('Bruno Back', 'Backend Developer', ['Go', 'Microservices', 'SQL'], 'Pleno'),
            ('Fernanda PM', 'Product Manager', ['Scrum', 'Jira', 'Liderança'], 'Sênior'),
            ('Rafael Sec', 'Analista de Segurança', ['Cybersecurity', 'Linux', 'Network'], 'Pleno'),
            ('Beatriz QA', 'QA Engineer', ['Selenium', 'Python', 'Testes'], 'Júnior'),
            ('Gustavo Cloud', 'Cloud Architect', ['Azure', 'Terraform', 'Python'], 'Sênior'),
            ('Larissa AI', 'Engenheira de IA', ['PyTorch', 'TensorFlow', 'NLP'], 'Pleno'),
            ('Roberto Legacy', 'Analista de Sistemas', ['Cobol', 'Java', 'SQL'], 'Sênior'),
        ]

        for i, (nome, headline, skills, nivel) in enumerate(candidatos_data):
            email = f'candidato{i+1}@teste.com'
            if not Usuario.objects.filter(email=email).exists():
                u = Usuario.objects.create_user(email, email, '123', first_name=nome.split()[0], last_name=nome.split()[1], tipo_usuario='candidato')
                c = Candidato.objects.create(usuario=u, cpf=f'111222333{i:02d}', headline=headline)
                
                # Resumo rico para IA
                Resumo_Profissional.objects.create(candidato=c, texto=f"Sou {nome}, profissional nível {nivel}. Tenho experiência sólida em {', '.join(skills)}. Busco oportunidades desafiadoras.")
                
                # Skills
                for s in skills:
                    Skill.objects.create(candidato=c, nome=s, tipo='hard')
                
                # Experiência Genérica
                Experiencia.objects.create(
                    candidato=c, cargo=headline, empresa='Empresa Anterior S.A.',
                    data_inicio=datetime.date(2022, 1, 1), data_fim=datetime.date(2024, 1, 1),
                    descricao=f'Atuei como {headline} utilizando {skills[0]} e {skills[1]}.'
                )

        self.stdout.write(self.style.SUCCESS('🚀 SEED ROBUSTO CONCLUÍDO! 15 Candidatos, 3 Empresas criados.'))