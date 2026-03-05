import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
from utils.parser import processar_arquivos
from utils.metricas import calcular_metricas, calcular_qualidade_arquivo
from utils.export import exportar_xlsx
from utils.analises import analisar_frete, analisar_motivos, analisar_ads, analisar_skus, simular_reducao
from utils.formatacao import formatar_brl, formatar_percentual, formatar_pct_direto, formatar_numero, formatar_risco
from utils.analise_anuncios import processar_analise_completa
from tab_analise_anuncios import render_tab_analise_anuncios
from tab_guia_uso import render_tab_guia_uso

# Configuração da página
st.set_page_config(
    page_title="Gestão de Devolução Inteligente",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado - TEMA LIQUID GLASS & VERDE MILITAR
st.markdown("""
    <style>
    /* Configurações Globais */
    .main {
        background-color: #000000;
    }
    
    [data-testid="stAppViewContainer"] {
        background-color: #000000;
    }

    /* Estilo dos Cartões de Métricas (Glass Effect) */
    .metric-card {
        background-color: rgba(255, 255, 255, 0.03);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
        flex: 1;
        position: relative;
        min-height: 110px;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        border-color: rgba(82, 121, 111, 0.5);
        background-color: rgba(82, 121, 111, 0.15);
        transform: translateY(-3px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }
    .metric-label {
        color: #888888;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 8px;
        letter-spacing: 0.5px;
    }
    .metric-value {
        color: #ffffff;
        font-size: 1.7rem;
        font-weight: 700;
    }
    .metric-subvalue {
        color: #888888;
        font-size: 0.8rem;
        margin-top: 4px;
    }
    .metric-icon {
        position: absolute;
        right: 20px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 2rem;
        color: #a0a0a0;
        opacity: 0.5;
    }
    
    /* Estilo das Seções de Gráficos (Glass Effect) */
    .chart-container {
        background-color: rgba(255, 255, 255, 0.03);
        padding: 25px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
        margin-bottom: 25px;
        transition: all 0.3s ease;
    }
    .chart-container:hover {
        border-color: rgba(82, 121, 111, 0.5);
        box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.9);
    }
    .chart-title {
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 25px;
        border-left: 4px solid rgba(82, 121, 111, 0.8);
        padding-left: 15px;
    }
    
    /* Estilo do Cabecalho de Filtros */
    .filter-header {
        background-color: rgba(255, 255, 255, 0.02);
        padding: 20px 30px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 25px;
    }
    
    /* Estilo do Simulador */
    .simulator-box {
        background-color: rgba(255, 255, 255, 0.03);
        padding: 25px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 25px;
    }
    
    /* Ajustes para Sidebar */
    [data-testid="stSidebar"] {
        background-color: #000000;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    [data-testid="stSidebar"] .stMarkdown h1, [data-testid="stSidebar"] .stMarkdown h2, [data-testid="stSidebar"] .stMarkdown h3 {
        color: #ffffff;
    }
    
    /* Estilo para os botões */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        background-color: rgba(82, 121, 111, 0.2) !important;
        color: #ffffff !important;
        border: 1px solid rgba(82, 121, 111, 0.5) !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background-color: rgba(82, 121, 111, 0.4) !important;
        border-color: rgba(82, 121, 111, 0.8) !important;
        transform: scale(1.02);
    }
    
    /* Estilo para o uploader na sidebar */
    [data-testid="stSidebar"] .stFileUploader {
        padding: 15px;
        background-color: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        border: 1px dashed rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }

    /* Estilização das Abas (Tabs) - Liquid Glass Style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        width: 100%;
        padding: 10px 0;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: nowrap;
        background-color: rgba(255, 255, 255, 0.02);
        border-radius: 10px;
        color: #888888;
        font-weight: 600;
        padding: 10px 25px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
        flex: 1;
        min-width: 150px;
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(82, 121, 111, 0.3) !important;
        color: #ffffff !important;
        border-color: rgba(82, 121, 111, 0.6) !important;
        box-shadow: 0 4px 15px rgba(82, 121, 111, 0.2);
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff;
        background-color: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.1);
    }

    /* Inputs e Selects */
    .stTextInput > div > div > input, .stSelectbox > div > div > div {
        background-color: rgba(255, 255, 255, 0.02) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

def render_metric_card(label, value, subvalue, icon):
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-subvalue">{subvalue}</div>
            <div class="metric-icon">{icon}</div>
        </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# Função de filtragem global dos dados
# ─────────────────────────────────────────────────────────
def aplicar_filtros(data, janela, canal, somente_ads, top10_skus, agrupar_por='SKU'):
    """
    Aplica os filtros globais do cabeçalho sobre os dados brutos.
    Retorna um dicionário com os mesmos campos de 'data', mas filtrados.
    """
    vendas = data['vendas'].copy()
    matriz = data['matriz'].copy() if data['matriz'] is not None else pd.DataFrame()
    full = data['full'].copy() if data['full'] is not None else pd.DataFrame()
    max_date = data['max_date']

    # 1) Filtro de JANELA (período)
    data_limite = max_date - timedelta(days=janela)
    if 'Data da venda' in vendas.columns:
        vendas = vendas[vendas['Data da venda'] >= data_limite]
    if 'Data da venda' in matriz.columns and len(matriz) > 0:
        matriz = matriz[matriz['Data da venda'] >= data_limite]
    if 'Data da venda' in full.columns and len(full) > 0:
        full = full[full['Data da venda'] >= data_limite]

    # 2) Filtro de CANAL
    if canal == 'Matriz':
        full = pd.DataFrame()
    elif canal == 'Full':
        matriz = pd.DataFrame()
    # 'Todos' mantém ambos

    # 3) Filtro SOMENTE ADS
    if somente_ads:
        if 'Venda por publicidade' in vendas.columns:
            vendas = vendas[vendas['Venda por publicidade'] == 'Sim']

    # 4) Filtro TOP 10 (filtra vendas apenas dos 10 itens com mais devoluções)
    if top10_skus:
        todas_dev = pd.concat([matriz, full], ignore_index=True)
        col_id = agrupar_por if agrupar_por in vendas.columns else 'SKU'
        
        if len(todas_dev) > 0 and 'N.º de venda' in todas_dev.columns and col_id in vendas.columns:
            # Mapear devoluções para itens via vendas
            dev_nums = set(todas_dev['N.º de venda'].astype(str).unique())
            vendas_com_dev = vendas[vendas['N.º de venda'].astype(str).isin(dev_nums)]
            
            if col_id in vendas_com_dev.columns:
                top_items = vendas_com_dev[col_id].value_counts().head(10).index.tolist()
                vendas = vendas[vendas[col_id].isin(top_items)]
                # Filtrar devoluções para manter apenas as relacionadas às vendas filtradas
                vendas_nums = set(vendas['N.º de venda'].astype(str).unique())
                if len(matriz) > 0 and 'N.º de venda' in matriz.columns:
                    matriz = matriz[matriz['N.º de venda'].astype(str).isin(vendas_nums)]
                if len(full) > 0 and 'N.º de venda' in full.columns:
                    full = full[full['N.º de venda'].astype(str).isin(vendas_nums)]

    return {
        'vendas': vendas,
        'matriz': matriz if len(matriz) > 0 else None,
        'full': full if len(full) > 0 else None,
        'max_date': max_date,
        'total_vendas': len(vendas),
        'total_matriz': len(matriz) if len(matriz) > 0 else 0,
        'total_full': len(full) if len(full) > 0 else 0,
    }

# ─────────────────────────────────────────────────────────
# Inicializar session state
# ─────────────────────────────────────────────────────────
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None

# ─────────────────────────────────────────────────────────
# SIDEBAR - UPLOAD E CONFIGURAÇÕES
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🚀 Gestão de Devolução Inteligente")
    st.markdown("---")
    
    st.subheader("📁 Upload de Dados")
    file_vendas = st.file_uploader("Relatório de Vendas", type=['xlsx'], key='vendas', help="Arraste o arquivo .xlsx de vendas do ML")
    file_devolucoes = st.file_uploader("Relatório de Devoluções", type=['xlsx'], key='devolucoes', help="Arraste o arquivo .xlsx de devoluções do ML")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        btn_processar = st.button("🚀 Processar", use_container_width=True, type="primary")
    with col_btn2:
        btn_exemplo = st.button("📋 Exemplo", use_container_width=True)
        
    if btn_processar:
        if file_vendas and file_devolucoes:
            with st.spinner("Processando..."):
                try:
                    data = processar_arquivos(file_vendas, file_devolucoes)
                    st.session_state.processed_data = data
                    st.success("Dados processados com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao processar arquivos: {str(e)}")
        else:
            st.warning("Por favor, suba ambos os arquivos.")

# ─────────────────────────────────────────────────────────
# CONTEÚDO PRINCIPAL
# ─────────────────────────────────────────────────────────
if st.session_state.processed_data is None:
    # Mostrar apenas a aba de Guia de Uso se não houver dados
    tab_guia = st.tabs(["📖 Guia de Uso"])[0]
    with tab_guia:
        render_tab_guia_uso()
else:
    data_raw = st.session_state.processed_data
    
    # Cabeçalho de Filtros Globais
    st.markdown('<div class="filter-header">', unsafe_allow_html=True)
    fc1, fc2, fc3, fc4, fc5 = st.columns([1.5, 1.2, 1, 1.2, 1.2])
    
    with fc5:
        visualizacao = st.selectbox("Agrupar por", ["SKU", "Título"], index=0, key="agrupar_por")
        agrupar_por = visualizacao
        
    with fc1:
        janela_opcoes = {'30 dias': 30, '60 dias': 60, '90 dias': 90, '120 dias': 120, '150 dias': 150, '180 dias': 180}
        janela_label = st.selectbox("Janela", list(janela_opcoes.keys()), index=5, key="filtro_janela")
        janela_global = janela_opcoes[janela_label]
    
    with fc2:
        canal_global = st.selectbox("Canal", ["Todos", "Matriz", "Full"], index=0, key="filtro_canal")
    
    with fc3:
        somente_ads_global = st.toggle("Somente Ads", value=False, key="filtro_ads")
    
    with fc4:
        top10_skus_global = st.toggle(f"Top 10 {visualizacao}s", value=False, key="filtro_top10")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Aplicar filtros globais
    data = aplicar_filtros(data_raw, janela_global, canal_global, somente_ads_global, top10_skus_global, agrupar_por=agrupar_por)
    
    # Garantir DataFrames válidos para funções
    df_matriz = data['matriz'] if data['matriz'] is not None else pd.DataFrame()
    df_full = data['full'] if data['full'] is not None else pd.DataFrame()
    
    st.markdown("---")
    
    # ─────────────────────────────────────────────────────
    # ABAS
    # ─────────────────────────────────────────────────────
    tab_guia, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "📖 Guia de Uso", "Resumo", "Janelas", "Matriz/Full", "Frete", 
        "Motivos", "Ads", "Anúncios", "Simulador", "IA Análise"
    ])
    
    # ─── TAB GUIA: GUIA DE USO ───
    with tab_guia:
        render_tab_guia_uso()
    
    # ─── TAB 1: RESUMO ───
    with tab1:
        metricas = calcular_metricas(data['vendas'], data['matriz'], data['full'], data['max_date'], janela_global)
        
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1:
            render_metric_card("VENDAS", formatar_numero(metricas['vendas']), f"{formatar_numero(metricas['unidades'])} un.", "🛒")
        with c2:
            render_metric_card("FATURAMENTO", formatar_brl(metricas['faturamento_produtos']), f"Total: {formatar_brl(metricas['faturamento_total'])}", "💲")
        with c3:
            render_metric_card("DEVOLUÇÕES", formatar_numero(metricas['devolucoes_vendas']), f"Taxa: {formatar_percentual(metricas['taxa_devolucao'])}", "🔄")
        with c4:
            render_metric_card("FAT. DEVOLUÇÕES", formatar_brl(metricas['faturamento_devolucoes']), "", "📉")
        with c5:
            render_metric_card("PERDA TOTAL", formatar_brl(metricas['perda_total']), "", "⚠️")
        with c6:
            render_metric_card("PERDA PARCIAL", formatar_brl(metricas['perda_parcial']), "", "📦")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">Classificação das Devoluções</div>', unsafe_allow_html=True)
            
            labels = ['Saudável', 'Crítica', 'Neutra']
            values = [metricas['saudaveis'], metricas['criticas'], metricas['neutras']]
            colors = ['#3b82f6', '#ef4444', '#10b981']
            
            fig_donut = go.Figure(data=[go.Pie(
                labels=labels, values=values, hole=.6,
                marker=dict(colors=colors),
                textinfo='label+percent' if sum(values) > 0 else 'none'
            )])
            fig_donut.update_layout(
                showlegend=False, 
                margin=dict(t=0, b=0, l=0, r=0), 
                height=300,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#ffffff')
            )
            st.plotly_chart(fig_donut, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_right:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="chart-title">Top 5 {visualizacao}s por Devoluções</div>', unsafe_allow_html=True)
            
            df_skus_top, _ = analisar_skus(data['vendas'], data['matriz'], data['full'], data['max_date'], janela_global, 5, agrupar_por=agrupar_por)
            
            if not df_skus_top.empty:
                col_y = agrupar_por if agrupar_por in df_skus_top.columns else df_skus_top.columns[0]
                df_skus_top = df_skus_top.sort_values('Dev.', ascending=True)
                fig_bar = go.Figure(go.Bar(
                    x=df_skus_top['Dev.'], y=df_skus_top[col_y],
                    orientation='h', marker_color='rgba(82, 121, 111, 0.8)'
                ))
                fig_bar.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=0, b=0, l=0, r=0), height=300,
                    xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                    yaxis=dict(showgrid=False),
                    font=dict(color='#ffffff')
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info(f"Sem dados de {visualizacao}s para exibir")
            st.markdown('</div>', unsafe_allow_html=True)

    # ─── TAB 2: JANELAS ───
    with tab2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Evolução da Taxa de Devolução</div>', unsafe_allow_html=True)
        
        # Simulação de dados para exemplo (substituir pela lógica real se disponível)
        df_evolucao = pd.DataFrame({
            'Data': pd.date_range(end=data['max_date'], periods=30),
            'Taxa': [metricas['taxa_devolucao']] * 30
        })
        
        fig_line = px.line(df_evolucao, x='Data', y='Taxa', markers=True)
        fig_line.update_traces(line_color='rgba(82, 121, 111, 1)', marker=dict(size=8))
        fig_line.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
            font=dict(color='#ffffff')
        )
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ─── TAB 3: MATRIZ/FULL ───
    with tab3:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Comparativo Matriz vs Full</div>', unsafe_allow_html=True)
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.write("**Matriz**")
            st.write(f"Vendas: {metricas['total_matriz']}")
        with col_m2:
            st.write("**Full**")
            st.write(f"Vendas: {metricas['total_full']}")
        st.markdown('</div>', unsafe_allow_html=True)

    # ─── TAB 4: FRETE ───
    with tab4:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Análise de Frete</div>', unsafe_allow_html=True)
        st.info("Funcionalidade em desenvolvimento")
        st.markdown('</div>', unsafe_allow_html=True)

    # ─── TAB 5: MOTIVOS ───
    with tab5:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Principais Motivos de Devolução</div>', unsafe_allow_html=True)
        st.info("Funcionalidade em desenvolvimento")
        st.markdown('</div>', unsafe_allow_html=True)

    # ─── TAB 6: ADS ───
    with tab6:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Impacto de Publicidade (Ads)</div>', unsafe_allow_html=True)
        st.info("Funcionalidade em desenvolvimento")
        st.markdown('</div>', unsafe_allow_html=True)

    # ─── TAB 7: ANÚNCIOS ───
    with tab7:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Análise de Anúncios</div>', unsafe_allow_html=True)
        st.info("Funcionalidade em desenvolvimento")
        st.markdown('</div>', unsafe_allow_html=True)

    # ─── TAB 8: SIMULADOR ───
    with tab8:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Simulador de Redução de Devoluções</div>', unsafe_allow_html=True)
        st.info("Funcionalidade em desenvolvimento")
        st.markdown('</div>', unsafe_allow_html=True)

    # ─── TAB 9: IA ANÁLISE ───
    with tab9:
        render_tab_analise_anuncios()
