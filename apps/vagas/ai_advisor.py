import google.generativeai as genai
import os
from django.conf import settings
from google.api_core import exceptions

def configurar_ia():
    try:
        # Pega a chave que configuramos no settings.py
        api_key = settings.GOOGLE_API_KEY
        
        if not api_key:
            print("❌ ERRO: GOOGLE_API_KEY não encontrada no settings.")
            return False
            
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        print(f"❌ Erro ao configurar IA: {e}")
        return False

def gerar_dicas_perfil(perfil_texto):
    if not configurar_ia():
        return "<ul><li>Erro de configuração da IA (Chave não detectada). Verifique as variáveis do Railway.</li></ul>"

    modelos = ['gemini-2.0-flash', 'gemini-2.0-flash-lite', 'gemini-1.5-flash']

    prompt = f"""
    Aja como um recrutador sênior de tecnologia.
    Analise o perfil abaixo e dê 3 dicas práticas (HTML <li> com <strong> no título) para melhorar o currículo.
    Perfil: "{perfil_texto}"
    """

    for modelo in modelos:
        try:
            print(f"Tentando modelo: {modelo}...")
            model = genai.GenerativeModel(modelo)
            response = model.generate_content(prompt)
            return response.text
        except:
            continue # Tenta o próximo se der erro
            
    return "<ul><li>O Vagalume AI está temporariamente indisponível. Tente novamente em instantes.</li></ul>"