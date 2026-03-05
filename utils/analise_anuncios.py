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
    
    # Se não encontrou ou é o valor de exemplo, tentar do ambiente
    if not api_key or "sua_chave" in api_key:
        api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        # Se não encontrar, o Streamlit mostrará um erro amigável
        st.error("🔑 **Erro de Configuração:** A chave `OPENAI_API_KEY` não foi encontrada. Por favor, adicione-a nos 'Secrets' do Streamlit Cloud.")
        st.info("Para configurar: Vá em Settings > Secrets e adicione: `OPENAI_API_KEY = \"sua_chave_aqui\"`")
        st.stop()
    
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
        
        # Verificar se foi redirecionado para login (bloqueio do ML)
        if 'login' in response.url.lower() or 'acesse sua conta' in response.text.lower():
            return {
                'url': url,
                'titulo': '',
                'preco': '',
                'descricao': '',
                'vendedor': '',
                'avaliacoes': '',
                'status': 'bloqueado',
                'mensagem': 'Mercado Livre bloqueou a requisição. A análise será feita apenas com o link.'
            }
        
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
        
        return dados
        
    except requests.exceptions.RequestException as e:
        return {
            'url': url,
            'status': 'bloqueado',
            'mensagem': f'Não foi possível acessar o link. A análise será feita apenas com o URL fornecido.'
        }
    except Exception as e:
        return {
            'url': url,
            'status': 'bloqueado',
            'mensagem': f'Erro ao processar o anúncio. A análise será feita apenas com o URL fornecido.'
        }

def analisar_anuncio_com_ia(dados_anuncio: Dict[str, Any], prompt_usuario: str, url: str) -> str:
    """
    Envia os dados do anúncio para a IA analisar com base no prompt do usuário.
    Se o scraping falhar, envia apenas o link.
    
    Args:
        dados_anuncio: Dicionário com dados extraídos do anúncio
        prompt_usuario: Prompt customizado do usuário
        url: URL do anúncio (usado como fallback)
        
    Returns:
        Análise da IA em formato de texto
    """
    try:
        client = get_openai_client()
        
        # Construir o contexto com os dados do anúncio
        if dados_anuncio.get('status') == 'bloqueado' or not dados_anuncio.get('titulo'):
            # Se foi bloqueado, enviar apenas o link
            contexto = f"""
Você é um especialista em análise de anúncios de e-commerce do Mercado Livre.

Não consegui extrair os dados do anúncio diretamente (o Mercado Livre bloqueou a requisição), 
mas aqui está o link do anúncio que você pode analisar:

**URL do Anúncio:** {url}

Por favor, acesse o link e faça uma análise completa seguindo o prompt abaixo:

{prompt_usuario}

Nota: Se você não conseguir acessar o link, forneça uma análise baseada na estrutura típica de anúncios do Mercado Livre 
e nas melhores práticas para o tipo de produto que pode estar neste URL.
"""
        else:
            # Se conseguiu extrair, enviar os dados
            contexto = f"""
Aqui estão os dados do anúncio para análise:

**Título:** {dados_anuncio.get('titulo', 'N/A')}
**Preço:** {dados_anuncio.get('preco', 'N/A')}
**Vendedor:** {dados_anuncio.get('vendedor', 'N/A')}
**Avaliações:** {dados_anuncio.get('avaliacoes', 'N/A')}
**Descrição:** {dados_anuncio.get('descricao', 'N/A')}
**URL:** {url}

---

Com base nesses dados e seguindo o prompt abaixo, faça uma análise completa:

{prompt_usuario}
"""
        
        # Fazer a chamada à API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
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
    
    # Analisar com IA (mesmo que o scraping tenha falhado)
    analise = analisar_anuncio_com_ia(dados, prompt_usuario, url)
    
    return {
        'status': 'sucesso',
        'dados_extraidos': dados,
        'analise_ia': analise
    }
