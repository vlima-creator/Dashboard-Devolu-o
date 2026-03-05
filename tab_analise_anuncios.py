import streamlit as st
from datetime import datetime
from utils.analise_anuncios import processar_analise_completa

def render_tab_analise_anuncios():
    """Renderiza a aba de Análise de Anúncios com IA"""
    
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Análise Inteligente de Anúncios com IA</div>', unsafe_allow_html=True)
    
    st.markdown("""
    Esta ferramenta utiliza **Google Gemini 1.5 Flash** (Gratuito) para analisar anúncios de produtos e identificar 
    pontos de melhoria que podem reduzir devoluções e aumentar conversões.
    """)
    
    # Aviso de configuração
    st.info("""
    🔑 **Primeira Vez?** Você precisa de uma chave de API do Google Gemini (gratuita). 
    
    **Como configurar:**
    1. Acesse [Google AI Studio](https://aistudio.google.com/app/apikey)
    2. Clique em "Create API Key"
    3. Copie a chave gerada
    4. No Streamlit Cloud: Settings > Secrets
    5. Cole: `GEMINI_API_KEY = "sua_chave_aqui"`
    6. Salve e recarregue o app
    """)
    
    # Seção de configuração
    st.markdown("### ⚙️ Configuração")
    
    url_anuncio = st.text_input(
        "Cole o link do anúncio (Mercado Livre ou similar)",
        placeholder="https://www.mercadolivre.com.br/...",
        key="url_anuncio_input"
    )
    
    st.markdown("### 📝 Prompt de Análise")
    st.markdown("O prompt abaixo está configurado para análise profunda de anúncios do Mercado Livre. Customize conforme necessário.")
    
    prompt_padrao = """Analise este anúncio do Mercado Livre e me entregue a resposta nas seções abaixo.

## Diagnóstico de RELEVÂNCIA NA BUSCA (relevância direta)
Liste o que está prejudicando a relevância em: título, categoria, atributos/ficha técnica, variações, catálogo (quando aplicável) e compliance/políticas.

## Diagnóstico de CONVERSÃO (relevância indireta)
Liste o que está prejudicando a conversão em: preço, entrega/logística, reputação, fotos, vídeos/clips, reviews e clareza da oferta.

## Top 10 melhorias prioritárias
Entregue uma lista numerada com as 10 melhorias mais importantes, em ordem de prioridade (1 = mais crítico).
Para cada item, informe:
- "O que fazer" (ação objetiva)
- "Por quê" (justificativa)
- "Impacto principal" (busca, conversão ou ambos).

## Sugestão de TÍTULOS
Sugira 1 título principal otimizado (até 60 caracteres) e 3 variações:
1. Variação mais genérica
2. Variação mais "cauda longa"
3. Variação com foco em benefício

Todos os títulos devem ter no máximo 60 caracteres e priorizar termos relevantes para busca.

## Preço, atacado e promoções
Avalie se faz sentido configurar Preço de Atacado (considerando público, ticket e margem) e sugira, quando fizer sentido, faixas de quantidade e preços coerentes.
Verifique se faz sentido ativar Promoção (considerando se já existe promoção no anúncio) e indique o melhor formato disponível e o cuidado para não depender só de desconto.

## Checklist final
Entregue um checklist em até 10 itens, no formato "[ ] ação", com tudo o que deve ser revisado antes de publicar/atualizar o anúncio.

### ⚠️ Regra importante sobre catálogo
Se este for um anúncio de catálogo, sinalize isso logo no início da resposta e NÃO sugira alterações em campos travados (como título ou ficha técnica padrão).
Foque apenas em melhorias possíveis em anúncios de catálogo (preço, atacado, promoções, logística, reputação, conteúdo complementar permitido, etc.)."""
    
    prompt_usuario = st.text_area(
        "Prompt de Análise",
        value=prompt_padrao,
        height=250,
        key="prompt_usuario_input"
    )
    
    # Botão de análise
    st.markdown("### 🚀 Executar Análise")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        btn_analisar = st.button("🔍 Analisar Anúncio", use_container_width=True, type="primary")
    with col2:
        btn_limpar = st.button("🗑️ Limpar", use_container_width=True)
    
    if btn_limpar:
        st.rerun()
    
    # Executar análise
    if btn_analisar:
        if not url_anuncio:
            st.error("❌ Por favor, cole um link válido do anúncio.")
        elif not prompt_usuario:
            st.error("❌ Por favor, insira um prompt de análise.")
        else:
            with st.spinner("⏳ Analisando anúncio... Isso pode levar alguns segundos."):
                try:
                    resultado = processar_analise_completa(url_anuncio, prompt_usuario)
                    
                    if resultado['status'] == 'erro':
                        st.error(f"❌ Erro ao processar: {resultado.get('mensagem', 'Erro desconhecido')}")
                    else:
                        # Exibir dados extraídos em um container destacado
                        st.markdown("---")
                        st.markdown("### 📊 Dados Extraídos do Anúncio")
                        
                        dados = resultado['dados_extraidos']
                        
                        # Mostrar aviso se houve bloqueio
                        if dados.get('status') == 'bloqueado':
                            st.warning(f"⚠️ **Nota:** {dados.get('mensagem', 'Não foi possível extrair todos os dados diretamente.')}")
                        
                        # Criar colunas para exibir os dados de forma organizada
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            with st.container(border=True):
                                st.markdown("**📌 Título**")
                                st.markdown(dados.get('titulo', '❌ Não foi possível extrair') or '❌ Não foi possível extrair')
                                
                                st.markdown("**💰 Preço**")
                                st.markdown(dados.get('preco', '❌ Não foi possível extrair') or '❌ Não foi possível extrair')
                                
                                st.markdown("**👤 Vendedor**")
                                st.markdown(dados.get('vendedor', '❌ Não foi possível extrair') or '❌ Não foi possível extrair')
                        
                        with col2:
                            with st.container(border=True):
                                st.markdown("**⭐ Avaliações**")
                                st.markdown(dados.get('avaliacoes', '❌ Não foi possível extrair') or '❌ Não foi possível extrair')
                                
                                st.markdown("**🔗 URL**")
                                st.markdown(f"[Acessar anúncio]({dados.get('url', '#')})")
                        
                        # Exibir descrição em um container separado
                        if dados.get('descricao'):
                            with st.container(border=True):
                                st.markdown("**📝 Descrição**")
                                st.markdown(dados.get('descricao'))
                        
                        # Exibir análise da IA em um container destacado
                        st.markdown("---")
                        st.markdown("### 🤖 Análise da IA")
                        
                        with st.container(border=True):
                            st.markdown(resultado['analise_ia'])
                        
                        # Adicionar informações de quando foi gerada
                        st.markdown(f"*Análise gerada em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}*")
                
                except Exception as e:
                    st.error(f"❌ Erro durante a análise: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Dicas de uso
    with st.expander("💡 Dicas de Uso"):
        st.markdown("""
        - **Link:** Funciona com anúncios do Mercado Livre, Amazon e outras plataformas
        - **Prompt:** O prompt padrão está otimizado para análise profunda de anúncios do Mercado Livre
        - **Análise:** A IA leva em conta o título, descrição, preço e avaliações do anúncio
        - **Visualização:** Toda a análise é exibida diretamente no painel para fácil visualização
        - **Histórico:** Você pode manter múltiplas análises abertas em abas diferentes do navegador para comparação
        - **Gratuito:** Usa o Google Gemini 1.5 Flash, que tem um plano gratuito generoso
        
        ### Possíveis problemas e soluções:
        - **Dados não extraídos:** O Mercado Livre pode estar bloqueando requisições. A IA ainda fornecerá análise baseada no link.
        - **Erro de API:** Verifique se a chave `GEMINI_API_KEY` está configurada corretamente nos Secrets do Streamlit.
        - **Análise incompleta:** Se os dados extraídos forem limitados, a IA ainda fornecerá recomendações baseadas no que conseguiu extrair.
        - **Limite de requisições:** O plano gratuito do Gemini permite muitas requisições por dia. Se atingir o limite, aguarde o reset.
        """)
