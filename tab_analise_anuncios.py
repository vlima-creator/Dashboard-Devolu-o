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
        - **Prompt:** O prompt padrão está otimizado para análise profunda de anúncios do Mercado Livre
        - **Análise:** A IA leva em conta o título, descrição, preço e avaliações do anúncio
        - **Exportação:** Você pode baixar a análise em Markdown para documentação ou compartilhamento
        - **Histórico:** Mantenha múltiplas análises abertas em abas diferentes do navegador para comparação
        """)
