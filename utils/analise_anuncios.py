import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os
import streamlit as st
from typing import Optional, Dict, Any
import json
import time

# Inicializar cliente OpenAI (usa OPENAI_API_KEY do ambiente ou st.secrets)
def get_openai_client():
    """Obtém o cliente OpenAI com a chave de API do ambiente ou st.secrets."""
    
    api_key = None
    
    # Tentar obter da st.secrets (Streamlit Cloud)
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
    except:
        pass
    
    # Se não encontrou, tentar do ambiente
    if not api_key:
        api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY não configurada. Por favor, configure a variável de ambiente ou adicione em st.secrets.")
    
    return OpenAI(api_key=api_key)

def extrair_dados_anuncio(url: str) -> Dict[str, Any]:
    """
    Extrai informações básicas de um anúncio do Mercado Livre.
    Usa múltiplas estratégias para evitar bloqueios.
    
    Args:
        url: URL do anúncio
        
    Returns:
        Dicionário com os dados extraídos
    """
    try:
        # Headers mais realistas para evitar bloqueios
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Fazer requisição com timeout maior
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extrair dados básicos
        dados = {
            'url': url,
            'titulo': '',
            'preco': '',
            'descricao': '',
            'vendedor': '',
            'avaliacoes': '',
            'status': 'sucesso'
        }
        
        # Estratégia 1: Tentar extrair título (múltiplas classes possíveis)
        titulo_elem = soup.find('h1', class_='ui-pdp-title')
        if not titulo_elem:
            titulo_elem = soup.find('h1')
        if titulo_elem:
            dados['titulo'] = titulo_elem.get_text(strip=True)
        
        # Estratégia 2: Tentar extrair preço (múltiplas classes possíveis)
        preco_elem = soup.find('span', class_='andes-money-amount__fraction')
        if not preco_elem:
            preco_elem = soup.find('span', {'class': lambda x: x and 'price' in x.lower()})
        if preco_elem:
            dados['preco'] = preco_elem.get_text(strip=True)
        
        # Estratégia 3: Tentar extrair descrição
        descricao_elem = soup.find('p', class_='ui-pdp-description__content')
        if not descricao_elem:
            descricao_elem = soup.find('div', {'class': lambda x: x and 'description' in x.lower()})
        if descricao_elem:
            dados['descricao'] = descricao_elem.get_text(strip=True)[:500]
        
        # Estratégia 4: Tentar extrair informações do vendedor
        vendedor_elem = soup.find('span', class_='ui-pdp-seller__name')
        if not vendedor_elem:
            vendedor_elem = soup.find('span', {'class': lambda x: x and 'seller' in x.lower()})
        if vendedor_elem:
            dados['vendedor'] = vendedor_elem.get_text(strip=True)
        
        # Estratégia 5: Tentar extrair avaliações
        avaliacoes_elem = soup.find('span', class_='ui-pdp-review__rating')
        if not avaliacoes_elem:
            avaliacoes_elem = soup.find('span', {'class': lambda x: x and 'rating' in x.lower()})
        if avaliacoes_elem:
            dados['avaliacoes'] = avaliacoes_elem.get_text(strip=True)
        
        # Se não conseguiu extrair muita informação, usar uma abordagem alternativa
        if not dados['titulo']:
            # Tentar extrair qualquer texto significativo
            all_text = soup.get_text()
            if all_text:
                # Pegar as primeiras linhas como título
                lines = [l.strip() for l in all_text.split('\n') if l.strip()]
                if lines:
                    dados['titulo'] = lines[0][:100]
        
        return dados
        
    except requests.exceptions.RequestException as e:
        return {
            'url': url,
            'status': 'erro',
            'mensagem': f'Erro ao acessar o link: {str(e)}. Verifique se o URL está correto e se o Mercado Livre não está bloqueando requisições.'
        }
    except Exception as e:
        return {
            'url': url,
            'status': 'erro',
            'mensagem': f'Erro ao processar o anúncio: {str(e)}'
        }

def analisar_anuncio_com_ia(dados_anuncio: Dict[str, Any], prompt_usuario: str) -> str:
    """
    Envia os dados do anúncio para a IA analisar com base no prompt do usuário.
    
    Args:
        dados_anuncio: Dicionário com dados extraídos do anúncio
        prompt_usuario: Prompt customizado do usuário
        
    Returns:
        Análise da IA em formato de texto
    """
    try:
        client = get_openai_client()
        
        # Construir o contexto com os dados do anúncio
        contexto = f"""
Aqui estão os dados do anúncio para análise:

**Título:** {dados_anuncio.get('titulo', 'N/A')}
**Preço:** {dados_anuncio.get('preco', 'N/A')}
**Vendedor:** {dados_anuncio.get('vendedor', 'N/A')}
**Avaliações:** {dados_anuncio.get('avaliacoes', 'N/A')}
**Descrição:** {dados_anuncio.get('descricao', 'N/A')}
**URL:** {dados_anuncio.get('url', 'N/A')}

---

Com base nesses dados e seguindo o prompt abaixo, faça uma análise completa:

{prompt_usuario}
"""
        
        # Fazer a chamada à API
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um especialista em análise de anúncios de e-commerce do Mercado Livre. Forneça análises detalhadas, estruturadas, acionáveis e em Markdown."
                },
                {
                    "role": "user",
                    "content": contexto
                }
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Erro ao analisar com IA: {str(e)}"

def processar_analise_completa(url: str, prompt_usuario: str) -> Dict[str, Any]:
    """
    Processa a análise completa: extrai dados e envia para IA.
    
    Args:
        url: URL do anúncio
        prompt_usuario: Prompt customizado
        
    Returns:
        Dicionário com dados extraídos e análise da IA
    """
    # Extrair dados do anúncio
    dados = extrair_dados_anuncio(url)
    
    if dados['status'] == 'erro':
        return dados
    
    # Analisar com IA
    analise = analisar_anuncio_com_ia(dados, prompt_usuario)
    
    return {
        'status': 'sucesso',
        'dados_extraidos': dados,
        'analise_ia': analise
    }
