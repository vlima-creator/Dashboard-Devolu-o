import streamlit as st
from datetime import datetime
from utils.analise_anuncios import processar_analise_completa

def render_tab_analise_anuncios():
    """Renderiza a aba de Análise de Anúncios com IA"""
    
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Análise Inteligente de Anúncios com IA</div>', unsafe_allow_html=True)
    
    st.markdown("""
    Esta ferramenta utiliza Inteligência Artificial para analisar anúncios de produtos e identificar 
    pontos de melhoria que podem reduzir devoluções e aumentar conversões.
    """)
    
    # Seção de configuração
    st.markdown("### ⚙️ Configuração")
    
    col_url, col_btn = st.columns([4, 1])
    with col_url:
        url_anuncio = st.text_input(
            "Cole o link do anúncio (Mercado Livre ou similar)",
            placeholder="https://www.mercadolivre.com.br/...",
            key="url_anuncio_input"
        )
    
    st.markdown("### 📝 Prompt de Análise")
    st.markdown("Customize o prompt abaixo ou use o padrão. O prompt será enviado junto com os dados do anúncio para a IA.")
    
    prompt_padrao = """Analise este anúncio de forma detalhada e identifique:
1. **Pontos Positivos**: O que está bem no anúncio
2. **Pontos Críticos**: Problemas que podem gerar devoluções
3. **Sugestões de Melhoria**: Ações específicas para melhorar o anúncio
4. **Impacto Estimado**: Como essas melhorias podem reduzir devoluções
5. **Prioridade**: Ordene as ações por impacto (Alto, Médio, Baixo)

Seja específico e acionável nas recomendações."""
    
    prompt_usuario = st.text_area(
        "Prompt de Análise",
        value=prompt_padrao,
        height=200,
        key="prompt_usuario_input"
    )
    
    # Botão de análise
    st.markdown("### 🚀 Executar Análise")
    
    col1, col2, col3 = st.columns([2, 1, 1])
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
                        # Exibir dados extraídos
                        st.markdown("### 📊 Dados Extraídos do Anúncio")
                        
                        dados = resultado['dados_extraidos']
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Título:** {dados.get('titulo', 'N/A')}")
                            st.markdown(f"**Preço:** {dados.get('preco', 'N/A')}")
                            st.markdown(f"**Vendedor:** {dados.get('vendedor', 'N/A')}")
                        
                        with col2:
                            st.markdown(f"**Avaliações:** {dados.get('avaliacoes', 'N/A')}")
                            st.markdown(f"**URL:** [{dados.get('url', 'N/A')[:50]}...]({dados.get('url', '#')})")
                        
                        if dados.get('descricao'):
                            st.markdown(f"**Descrição:** {dados.get('descricao')}")
                        
                        # Exibir análise da IA
                        st.markdown("### 🤖 Análise da IA")
                        st.markdown(resultado['analise_ia'])
                        
                        # Botão para exportar análise
                        st.markdown("---")
                        analise_texto = f"""# Análise de Anúncio - {dados.get('titulo', 'Sem título')}

## Dados do Anúncio
- **URL:** {dados.get('url', 'N/A')}
- **Preço:** {dados.get('preco', 'N/A')}
- **Vendedor:** {dados.get('vendedor', 'N/A')}
- **Avaliações:** {dados.get('avaliacoes', 'N/A')}

## Análise
{resultado['analise_ia']}

---
Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
                        
                        st.download_button(
                            label="📥 Baixar Análise (Markdown)",
                            data=analise_texto,
                            file_name=f"analise_anuncio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                
                except Exception as e:
                    st.error(f"❌ Erro durante a análise: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Dicas de uso
    with st.expander("💡 Dicas de Uso"):
        st.markdown("""
        - **Link:** Funciona com anúncios do Mercado Livre, Amazon e outras plataformas
        - **Prompt:** Customize o prompt para focar em diferentes aspectos (qualidade, preço, descrição, etc.)
        - **Análise:** A IA leva em conta o título, descrição, preço e avaliações do anúncio
        - **Histórico:** Você pode manter múltiplas análises abertas em abas diferentes do navegador
        """)
