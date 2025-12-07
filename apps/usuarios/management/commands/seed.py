from django.core.management.base import BaseCommand
from apps.usuarios.models import Usuario, Candidato, Empresa, Recrutador, Skill, Experiencia, Resumo_Profissional
from apps.vagas.models import Vaga, Plano
import datetime

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de teste (Seed)'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Iniciando o Seeding do Banco de Dados...')

        # ---------------------------------------------------------
        # 0. CRIAR SUPERUSUÁRIO (ADMIN) - ADICIONADO AGORA
        # ---------------------------------------------------------
        if not Usuario.objects.filter(email='admin@vagalume.com').exists():
            Usuario.objects.create_superuser(
                username='admin@vagalume.com',
                email='admin@vagalume.com',
                password='admin', # Senha do Painel Admin
                first_name='Super',
                last_name='Admin'
            )
            self.stdout.write(self.style.SUCCESS('✅ Admin criado: admin@vagalume.com / admin'))

        # ---------------------------------------------------------
        # 1. CRIAR PLANOS
        # ---------------------------------------------------------
        planos = [
            {'chave': 'basico', 'nome': 'Básico (Grátis)', 'preco': 0.00, 'limite': 1},
            {'chave': 'intermediario', 'nome': 'Intermediário', 'preco': 150.00, 'limite': 10},
            {'chave': 'premium', 'nome': 'Premium', 'preco': 400.00, 'limite': 999},
        ]
        
        for p in planos:
            Plano.objects.get_or_create(
                nome_chave=p['chave'],
                defaults={
                    'nome_exibicao': p['nome'],
                    'preco': p['preco'],
                    'limite_vagas': p['limite']
                }
            )
        self.stdout.write(self.style.SUCCESS('✅ Planos criados.'))

        # ---------------------------------------------------------
        # 2. CRIAR EMPRESA (Vagalume Tech)
        # ---------------------------------------------------------
        empresa, created = Empresa.objects.get_or_create(
            cnpj='12345678000199',
            defaults={
                'nome': 'Vagalume Tech',
                'setor': 'Tecnologia',
                'telefone': '11999998888',
                'plano_assinado': 'premium' 
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Empresa "Vagalume Tech" criada.'))
        else:
            self.stdout.write('ℹ️ Empresa já existia.')

        # ---------------------------------------------------------
        # 3. CRIAR RECRUTADOR (Dono da Vagalume)
        # ---------------------------------------------------------
        email_recrutador = 'recrutador@vagalume.com'
        
        if not Usuario.objects.filter(email=email_recrutador).exists():
            user_rec = Usuario.objects.create_user(
                username=email_recrutador,
                email=email_recrutador,
                password='123',
                first_name='Chefe',
                last_name='Recrutador',
                tipo_usuario='recrutador'
            )
            Recrutador.objects.create(usuario=user_rec, empresa=empresa)
            self.stdout.write(self.style.SUCCESS(f'✅ Recrutador criado: {email_recrutador} (Senha: 123)'))
        else:
            self.stdout.write(f'ℹ️ Recrutador {email_recrutador} já existe.')

        # ---------------------------------------------------------
        # 4. CRIAR VAGA
        # ---------------------------------------------------------
        titulo_vaga = 'Desenvolvedor Python Junior'
        
        if not Vaga.objects.filter(titulo=titulo_vaga).exists():
            recrutador = Recrutador.objects.get(usuario__email=email_recrutador)
            Vaga.objects.create(
                empresa=empresa,
                recrutador=recrutador,
                titulo=titulo_vaga,
                area_atuacao='tecnologia',
                descricao='Estamos buscando um dev apaixonado por Django, APIs e Inteligência Artificial para inovar no mercado de RH.',
                requisitos='Python, Django, SQL, Git e vontade de aprender.',
                tipo_contrato='CLT',
                localidade='São Paulo - SP (Híbrido)',
                faixa_salarial='R$ 4.000 - R$ 5.000',
                status=True
            )
            self.stdout.write(self.style.SUCCESS('✅ Vaga criada.'))
        else:
            self.stdout.write('ℹ️ Vaga já existia.')

        # ---------------------------------------------------------
        # 5. CRIAR CANDIDATO (João Python)
        # ---------------------------------------------------------
        email_candidato = 'candidato@vagalume.com'
        
        if not Usuario.objects.filter(email=email_candidato).exists():
            user_cand = Usuario.objects.create_user(
                username=email_candidato,
                email=email_candidato,
                password='123',
                first_name='João',
                last_name='Python',
                tipo_usuario='candidato'
            )
            
            candidato = Candidato.objects.create(
                usuario=user_cand,
                cpf='11122233344',
                headline='Desenvolvedor Backend Python | Django'
            )
            
            Resumo_Profissional.objects.create(
                candidato=candidato,
                texto="Sou um desenvolvedor focado em backend com Python. Tenho experiência prática na criação de APIs RESTful com Django e integração com serviços de Inteligência Artificial. Gosto de resolver problemas complexos e otimizar queries SQL. Busco minha primeira oportunidade júnior para crescer junto com a empresa."
            )
            
            skills = ['Python', 'Django', 'PostgreSQL', 'Git', 'APIs REST', 'Docker']
            for s in skills:
                Skill.objects.create(candidato=candidato, nome=s, tipo='hard')
                
            Experiencia.objects.create(
                candidato=candidato,
                cargo='Estagiário de Desenvolvimento',
                empresa='StartUp Inovadora',
                data_inicio=datetime.date(2023, 1, 1),
                data_fim=datetime.date(2024, 1, 1),
                descricao='Atuei na manutenção de sistemas legados em Python, correção de bugs e auxiliei na migração de banco de dados para PostgreSQL.'
            )

            self.stdout.write(self.style.SUCCESS(f'✅ Candidato criado: {email_candidato} (Senha: 123)'))
        else:
            self.stdout.write(f'ℹ️ Candidato {email_candidato} já existe.')

        self.stdout.write(self.style.SUCCESS('🚀 SEEDING CONCLUÍDO! O BANCO ESTÁ PRONTO PARA A APRESENTAÇÃO.'))