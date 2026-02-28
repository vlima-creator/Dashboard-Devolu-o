import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from utils.parser import processar_arquivos
from utils.metricas import calcular_metricas, calcular_qualidade_arquivo
from utils.export import exportar_xlsx
from utils.analises import analisar_frete, analisar_motivos, analisar_ads, analisar_skus, simular_reducao
from utils.formatacao import formatar_brl, formatar_percentual, formatar_numero

# Configuração da página
st.set_page_config(
    page_title="Dashboard Vendas x Devoluções",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None

# Sidebar
st.sidebar.title("📊 Dashboard Vendas x Devoluções")
st.sidebar.markdown("---")

# Página inicial ou dashboard
if st.session_state.processed_data is None:
    # PÁGINA DE UPLOAD
    st.title("📊 Dashboard Vendas x Devoluções")
    st.markdown("Análise automática de Vendas e Devoluções do Mercado Livre (BR)")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📁 Relatório de Vendas")
        st.markdown("Aba: **Vendas BR**")
        file_vendas = st.file_uploader("Selecione o arquivo de Vendas", type=['xlsx'], key='vendas')
    
    with col2:
        st.subheader("📁 Relatório de Devoluções")
        st.markdown("Abas: **devoluções vendas matriz** e **devoluções vendas full**")
        file_devolucoes = st.file_uploader("Selecione o arquivo de Devoluções", type=['xlsx'], key='devolucoes')
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Processar", use_container_width=True, type="primary"):
            if file_vendas and file_devolucoes:
                with st.spinner("Processando arquivos..."):
                    try:
                        data = processar_arquivos(file_vendas, file_devolucoes)
                        st.session_state.processed_data = data
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao processar: {str(e)}")
            else:
                st.warning("Por favor, selecione ambos os arquivos")
    
    with col2:
        if st.button("📋 Carregar Exemplo", use_container_width=True):
            with st.spinner("Carregando exemplo..."):
                try:
                    # Tentar carregar arquivos de exemplo
                    import os
                    example_dir = "public/examples"
                    
                    if os.path.exists(f"{example_dir}/vendas_exemplo.xlsx") and os.path.exists(f"{example_dir}/devolucoes_exemplo.xlsx"):
                        with open(f"{example_dir}/vendas_exemplo.xlsx", 'rb') as f1:
                            with open(f"{example_dir}/devolucoes_exemplo.xlsx", 'rb') as f2:
                                data = processar_arquivos(f1, f2)
                                st.session_state.processed_data = data
                                st.rerun()
                    else:
                        st.warning("Arquivos de exemplo não encontrados")
                except Exception as e:
                    st.error(f"Erro ao carregar exemplo: {str(e)}")
    
    st.markdown("---")
    
    with st.expander("ℹ️ Como usar"):
        st.markdown("""
        1. **Selecione o arquivo de Vendas** (aba "Vendas BR")
        2. **Selecione o arquivo de Devoluções** (abas "devoluções vendas matriz" e "devoluções vendas full")
        3. **Clique em "Processar"** para gerar a análise
        4. **Ou clique em "Carregar Exemplo"** para ver uma demonstração
        
        ### Colunas obrigatórias:
        
        **Vendas:**
        - N.º de venda
        - Data da venda
        - SKU
        - Receita por produtos (BRL)
        - Receita por envio (BRL)
        
        **Devoluções:**
        - N.º de venda
        - Estado
        - Motivo do resultado
        - Cancelamentos e reembolsos (BRL)
        """)

else:
    # DASHBOARD
    data = st.session_state.processed_data
    
    # Header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("📊 Dashboard Vendas x Devoluções")
        st.markdown(f"Referência: {data['max_date'].strftime('%d/%m/%Y')} | Janela padrão: 180 dias")
    
    with col2:
        if st.button("← Voltar", use_container_width=True):
            st.session_state.processed_data = None
            st.rerun()
    
    st.markdown("---")
    
    # Info banner
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Linhas de Vendas", f"{data['total_vendas']:,}")
    with col2:
        st.metric("Devoluções Matriz", f"{data['total_matriz']:,}")
    with col3:
        st.metric("Devoluções Full", f"{data['total_full']:,}")
    
    # Abas
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📈 Resumo",
        "🎯 Janelas",
        "📦 Matriz/Full",
        "🚚 Frete",
        "🔍 Motivos",
        "📢 Ads",
        "📊 SKUs",
        "🎮 Simulador"
    ])
    
    # TAB 1: RESUMO
    with tab1:
        st.subheader("Resumo Executivo - 180 dias")
        
        metricas = calcular_metricas(data['vendas'], data['matriz'], data['full'], data['max_date'], 180)
        qualidade = calcular_qualidade_arquivo(data)
        
        # Qualidade do Arquivo
        st.subheader("🔍 Qualidade do Arquivo")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Vendas sem número (%)", formatar_percentual(qualidade['vendas']['sem_numero_pct']/100))
        with col2:
            st.metric("Vendas sem data (%)", formatar_percentual(qualidade['vendas']['sem_data_pct']/100))
        with col3:
            st.metric("Vendas sem receita (%)", formatar_percentual(qualidade['vendas']['sem_receita_pct']/100))
        
        # KPIs
        st.subheader("📊 KPIs Principais")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Vendas", formatar_numero(metricas['vendas']))
        with col2:
            st.metric("Faturamento Total", formatar_brl(metricas['faturamento_total']))
        with col3:
            st.metric("Taxa de Devolução", formatar_percentual(metricas['taxa_devolucao']))
        with col4:
            st.metric("Impacto Financeiro", formatar_brl(metricas['impacto_devolucao']))
        
        # Detalhes
        st.subheader("📈 Detalhes")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Devoluções", formatar_numero(metricas['devolucoes_vendas']))
        with col2:
            st.metric("Perda Total", formatar_brl(metricas['perda_total']))
        with col3:
            st.metric("Perda Parcial", formatar_brl(metricas['perda_parcial']))
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Saudáveis", metricas['saudaveis'])
        with col2:
            st.metric("Críticas", metricas['criticas'])
        with col3:
            st.metric("Neutras", metricas['neutras'])
    
    # TAB 2: JANELAS
    with tab2:
        st.subheader("Análise por Janelas de Tempo")
        
        janelas_data = []
        for janela in [30, 60, 90, 120, 150, 180]:
            m = calcular_metricas(data['vendas'], data['matriz'], data['full'], data['max_date'], janela)
            janelas_data.append({
                'Período': f'{janela}d',
                'Vendas': formatar_numero(m['vendas']),
                'Taxa (%)': formatar_percentual(m['taxa_devolucao']),
                'Devoluções': formatar_numero(m['devolucoes_vendas']),
                'Impacto (R$)': formatar_brl(m['impacto_devolucao']),
            })
        
        df_janelas = pd.DataFrame(janelas_data)
        
        # Gráfico
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_janelas['Período'], y=df_janelas['Taxa (%)'], mode='lines+markers', name='Taxa de Devolução (%)', line=dict(color='red', width=3)))
        fig.update_layout(title="Evolução da Taxa de Devolução", xaxis_title="Período", yaxis_title="Taxa (%)", height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela
        st.dataframe(df_janelas, use_container_width=True, hide_index=True)
    
    # TAB 3: MATRIZ/FULL
    with tab3:
        st.subheader("Comparação Matriz vs Full")
        
        total_matriz = len(data['matriz']) if data['matriz'] is not None else 0
        total_full = len(data['full']) if data['full'] is not None else 0
        total = total_matriz + total_full
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Devoluções Matriz", formatar_numero(total_matriz))
        with col2:
            st.metric("Devoluções Full", formatar_numero(total_full))
        with col3:
            st.metric("Total", formatar_numero(total))
        
        # Gráfico
        fig = go.Figure(data=[
            go.Bar(x=['Matriz', 'Full'], y=[total_matriz, total_full], marker_color=['#3b82f6', '#ef4444'])
        ])
        fig.update_layout(title="Devoluções por Canal", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # TAB 4: FRETE
    with tab4:
        st.subheader("🚚 Análise de Frete e Forma de Entrega")
        
        janela_frete = st.slider("Período (dias)", 30, 180, 180, key="frete_janela")
        
        df_frete = analisar_frete(data['vendas'], data['matriz'], data['full'], data['max_date'], janela_frete)
        
        if len(df_frete) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de taxa por forma de entrega
                fig = px.bar(df_frete, x='Forma de Entrega', y='Taxa (%)', 
                            title='Taxa de Devolução por Forma de Entrega',
                            color='Taxa (%)', color_continuous_scale='Reds')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Gráfico de impacto financeiro
                fig = px.bar(df_frete, x='Forma de Entrega', y='Impacto (R$)',
                            title='Impacto Financeiro por Forma de Entrega',
                            color='Impacto (R$)', color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df_frete, use_container_width=True, hide_index=True)
        else:
            st.warning("Sem dados disponíveis para análise de frete")
    
    # TAB 5: MOTIVOS
    with tab5:
        st.subheader("🔍 Análise de Motivos de Devolução")
        
        janela_motivos = st.slider("Período (dias)", 30, 180, 180, key="motivos_janela")
        
        df_motivos = analisar_motivos(data['matriz'], data['full'], data['max_date'], janela_motivos)
        
        if len(df_motivos) > 0:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Gráfico de pizza
                fig = px.pie(df_motivos, values='Quantidade', names='Motivo',
                            title='Distribuição de Motivos de Devolução')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Tabela
                st.dataframe(df_motivos, use_container_width=True, hide_index=True)
        else:
            st.warning("Sem dados disponíveis para análise de motivos")
    
    # TAB 6: ADS
    with tab6:
        st.subheader("📢 Análise de Vendas por Publicidade")
        
        janela_ads = st.slider("Período (dias)", 30, 180, 180, key="ads_janela")
        
        df_ads = analisar_ads(data['vendas'], data['matriz'], data['full'], data['max_date'], janela_ads)
        
        if len(df_ads) > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                com_pub = df_ads[df_ads['Tipo'].str.contains('Com')]['Vendas'].values[0] if any(df_ads['Tipo'].str.contains('Com')) else 0
                st.metric("Com Publicidade", formatar_numero(com_pub))
            with col2:
                sem_pub = df_ads[df_ads['Tipo'].str.contains('Sem')]['Vendas'].values[0] if any(df_ads['Tipo'].str.contains('Sem')) else 0
                st.metric("Sem Publicidade", formatar_numero(sem_pub))
            with col3:
                st.metric("Total de Vendas", formatar_numero(df_ads['Vendas'].sum()))
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de taxa
                fig = px.bar(df_ads, x='Tipo', y='Taxa (%)',
                            title='Taxa de Devolução por Tipo de Publicidade',
                            color='Taxa (%)', color_continuous_scale='Reds')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Gráfico de impacto
                fig = px.bar(df_ads, x='Tipo', y='Impacto (R$)',
                            title='Impacto Financeiro por Tipo de Publicidade',
                            color='Impacto (R$)', color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df_ads, use_container_width=True, hide_index=True)
        else:
            st.warning("Sem dados disponíveis para análise de publicidade")
    
    # TAB 7: SKUS
    with tab7:
        st.subheader("📊 Análise de SKUs com Maior Risco")
        
        col1, col2 = st.columns(2)
        
        with col1:
            janela_skus = st.slider("Período (dias)", 30, 180, 180, key="skus_janela")
        with col2:
            top_n = st.slider("Top N SKUs", 5, 20, 10, key="skus_top")
        
        df_skus = analisar_skus(data['vendas'], data['matriz'], data['full'], data['max_date'], janela_skus, top_n)
        
        if len(df_skus) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de taxa
                fig = px.bar(df_skus, x='SKU', y='Taxa (%)',
                            title='Taxa de Devolução por SKU',
                            color='Taxa (%)', color_continuous_scale='Reds')
                fig.update_xaxes(tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Gráfico de impacto
                fig = px.bar(df_skus, x='SKU', y='Impacto (R$)',
                            title='Impacto Financeiro por SKU',
                            color='Impacto (R$)', color_continuous_scale='Blues')
                fig.update_xaxes(tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df_skus, use_container_width=True, hide_index=True)
        else:
            st.warning("Sem dados disponíveis para análise de SKUs")
    
    # TAB 8: SIMULADOR
    with tab8:
        st.subheader("🎮 Simulador de Redução de Devoluções")
        
        col1, col2 = st.columns(2)
        
        with col1:
            janela_sim = st.slider("Período (dias)", 30, 180, 180, key="sim_janela")
        with col2:
            reducao = st.slider("Redução desejada (%)", 0, 100, 10, key="sim_reducao")
        
        resultado = simular_reducao(data['vendas'], data['matriz'], data['full'], data['max_date'], janela_sim, reducao)
        
        # Mostrar cenários
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Vendas Totais", formatar_numero(resultado['vendas_totais']))
        with col2:
            st.metric("Faturamento Total", formatar_brl(resultado['faturamento_total']))
        with col3:
            st.metric("Economia Potencial", formatar_brl(resultado['economia']), delta=formatar_percentual(reducao/100))
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Cenário Atual")
            st.metric("Devoluções", resultado['cenario_atual']['devolucoes'])
            st.metric("Taxa de Devolução", f"{resultado['cenario_atual']['taxa']:.2f}%")
            st.metric("Impacto Financeiro", f"R$ {resultado['cenario_atual']['impacto']/1000:.1f}k")
        
        with col2:
            st.subheader("🎯 Cenário Simulado (-{:.0f}%)".format(reducao))
            st.metric("Devoluções", resultado['cenario_simulado']['devolucoes'])
            st.metric("Taxa de Devolução", f"{resultado['cenario_simulado']['taxa']:.2f}%")
            st.metric("Impacto Financeiro", f"R$ {resultado['cenario_simulado']['impacto']/1000:.1f}k")
        
        # Gráfico de comparação
        comparacao_data = {
            'Cenário': ['Atual', 'Simulado'],
            'Devoluções': [resultado['cenario_atual']['devolucoes'], resultado['cenario_simulado']['devolucoes']],
            'Taxa (%)': [resultado['cenario_atual']['taxa'], resultado['cenario_simulado']['taxa']],
        }
        df_comparacao = pd.DataFrame(comparacao_data)
        
        fig = px.bar(df_comparacao, x='Cenário', y=['Devoluções', 'Taxa (%)'],
                    title='Comparação de Cenários',
                    barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    
    # Export
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Exportar XLSX", use_container_width=True, type="primary"):
            try:
                xlsx_file = exportar_xlsx(data)
                st.download_button(
                    label="⬇️ Baixar Arquivo",
                    data=xlsx_file,
                    file_name=f"Dashboard_Vendas_Devolucoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Erro ao exportar: {str(e)}")
    
    with col2:
        if st.button("🔄 Processar Novo Arquivo", use_container_width=True):
            st.session_state.processed_data = None
            st.rerun()
