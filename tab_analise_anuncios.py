import streamlit as st
from datetime import datetime
from utils.analise_anuncios import processar_analise_completa
from utils.export_anuncio_pdf import gerar_pdf_analise_anuncio

def render_tab_analise_anuncios():
    """Renderiza a aba de Análise de Anúncios com IA"""
    
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Análise Inteligente de Anúncios com IA</div>', unsafe_allow_html=True)
    
    # Seção de configuração
    st.markdown("### ⚙️ Configuração")
    
    url_anuncio = st.text_input(
        "Cole o link do anúncio (Mercado Livre ou similar)",
        placeholder="https://www.mercadolivre.com.br/...",
        key="url_anuncio_input"
    )
    
    # Prompt de análise em um expander
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
    
    with st.expander("📝 Prompt de Análise (Customizável)"):
        prompt_usuario = st.text_area(
            "Prompt de Análise",
            value=prompt_padrao,
            height=250,
            key="prompt_usuario_input"
        )
    
    # Se o expander não foi aberto, usar o prompt padrão
    if 'prompt_usuario_input' not in st.session_state:
        prompt_usuario = prompt_padrao
    else:
        prompt_usuario = st.session_state.get('prompt_usuario_input', prompt_padrao)
    
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
        else:
            # Usar o prompt do session_state se foi customizado, senão usar o padrão
            prompt_final = st.session_state.get('prompt_usuario_input', prompt_padrao)
            
            with st.spinner("⏳ Analisando anúncio... Isso pode levar alguns segundos."):
                try:
                    resultado = processar_analise_completa(url_anuncio, prompt_final)
                    
                    if resultado['status'] == 'erro':
                        st.error(f"❌ Erro ao processar: {resultado.get('mensagem', 'Erro desconhecido')}")
                    else:
                        # Exibir análise da IA em um container destacado
                        st.markdown("---")
                        st.markdown("### 🤖 Análise da IA")
                        
                        with st.container(border=True):
                            st.markdown(resultado['analise_ia'])
                        
                        # Adicionar informações de quando foi gerada
                        st.markdown(f"*Análise gerada em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}*")
                        
                        # Botão para gerar PDF
                        st.markdown("---")
                        st.markdown("### 📥 Exportar Relatório")
                        
                        try:
                            # Gerar PDF
                            pdf_bytes = gerar_pdf_analise_anuncio(
                                dados_anuncio=resultado['dados_extraidos'],
                                analise_ia=resultado['analise_ia'],
                                url=url_anuncio
                            )
                            
                            # Botão de download
                            st.download_button(
                                label="📄 Baixar Relatório em PDF",
                                data=pdf_bytes,
                                file_name=f"analise_anuncio_{datetime.now().strftime('%d_%m_%Y_%H_%M_%S')}.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                                type="primary"
                            )
                            
                            st.success("✅ PDF pronto para download! Clique no botão acima para baixar o relatório completo.")
                            
                        except Exception as e:
                            st.error(f"❌ Erro ao gerar PDF: {str(e)}")
                
                except Exception as e:
                    st.error(f"❌ Erro durante a análise: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Dicas de uso
    with st.expander("💡 Dicas de Uso"):
        st.markdown("""
        - **Link:** Funciona com anúncios do Mercado Livre, Amazon e outras plataformas
        - **Prompt:** O prompt padrão está otimizado para análise profunda de anúncios do Mercado Livre
        - **PDF:** Você pode exportar a análise completa em PDF para compartilhar ou arquivar
        - **Histórico:** Você pode manter múltiplas análises abertas em abas diferentes do navegador para comparação
        """)
