# Arquivo: apps/matching/engine.py (VERSÃO "TAGS")

# Não precisamos mais de sklearn!
from apps.usuarios.models import Candidato, Resumo_Profissional, Skill, Experiencia
from apps.vagas.models import Vaga

# Esta função é chamada pelo "Radar de Talentos" E pelo "Ver Candidatos"
def get_tags_candidato(candidato):
    """
    Pega a "lista de tags" de um candidato.
    """
    tags = set()
    
    # Pega todas as skills do modelo Skill
    skills = [skill.nome.lower().strip() for skill in candidato.skills.all()]
    tags.update(skills)
    
    # (Opcional, mas bom) Pega os cargos das experiências
    cargos = [exp.cargo.lower().strip() for exp in candidato.experiencias.all()]
    tags.update(cargos)
    
    return tags

# Esta função é chamada pelo "Radar de Talentos" E pelo "Ver Candidatos"
def get_tags_vaga(vaga):
    """
    Pega a "lista de tags" de uma vaga.
    Vamos assumir que o recrutador as escreveu no campo 'requisitos',
    separadas por vírgula.
    """
    tags = set()
    
    texto_requisitos = vaga.requisitos.lower()
    lista_tags = [tag.strip() for tag in texto_requisitos.split(',')]
    
    palavras_titulo = [palavra.strip() for palavra in vaga.titulo.lower().split()]

    tags.update(lista_tags)
    tags.update(palavras_titulo)
    
    tags.discard("") # Remove tags vazias
    
    return tags

# Esta função é chamada pelo "Radar de Talentos" E pelo "Ver Candidatos"
def calcular_similaridade_tags(vaga, candidato):
    """
    A "Engine" de Tags!
    Calcula o "Índice de Jaccard" (Interseção / União).
    """
    tags_vaga = get_tags_vaga(vaga)
    tags_candidato = get_tags_candidato(candidato)

    if not tags_vaga or not tags_candidato:
        return 0 # Não dá para comparar listas vazias
        
    intersecao = tags_vaga.intersection(tags_candidato)
    uniao = tags_vaga.union(tags_candidato)
    
    score = len(intersecao) / len(uniao)
    
    return round(score * 100)