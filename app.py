import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Devoluções BlueWorks",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos customizados
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .metric-title {
        font-size: 0.875rem;
        color: #666;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1f77b4;
        margin-top: 0.5rem;
    }
    .metric-change {
        font-size: 0.875rem;
        color: #666;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Carregar dados
@st.cache_data
def load_data():
    excel_file = "Analise_Devolucoes_x_Vendas_BlueWorks_6m.xlsx"
    
    # Leitura de todas as abas
    resumo = pd.read_excel(excel_file, sheet_name="Resumo_Janelas")
    saudavel_critica = pd.read_excel(excel_file, sheet_name="Saudavel_vs_Critica_180d")
    matriz_full = pd.read_excel(excel_file, sheet_name="Matriz_vs_Full_180d")
    frete = pd.read_excel(excel_file, sheet_name="Frete_180d")
    motivos = pd.read_excel(excel_file, sheet_name="Motivos_180d")
    top10_devol = pd.read_excel(excel_file, sheet_name="Top10_Devol_Qtd_180d")
    top10_taxa = pd.read_excel(excel_file, sheet_name="Top10_Taxa_180d")
    top10_perdas = pd.read_excel(excel_file, sheet_name="Top10_Perdas_180d")
    top10_risco = pd.read_excel(excel_file, sheet_name="Top10_Risco_180d")
    risco_30d = pd.read_excel(excel_file, sheet_name="Risco_SKU_30d")
    risco_60d = pd.read_excel(excel_file, sheet_name="Risco_SKU_60d")
    risco_90d = pd.read_excel(excel_file, sheet_name="Risco_SKU_90d")
    risco_120d = pd.read_excel(excel_file, sheet_name="Risco_SKU_120d")
    risco_150d = pd.read_excel(excel_file, sheet_name="Risco_SKU_150d")
    risco_180d = pd.read_excel(excel_file, sheet_name="Risco_SKU_180d")
    
    return {
        "resumo": resumo,
        "saudavel_critica": saudavel_critica,
        "matriz_full": matriz_full,
        "frete": frete,
        "motivos": motivos,
        "top10_devol": top10_devol,
        "top10_taxa": top10_taxa,
        "top10_perdas": top10_perdas,
        "top10_risco": top10_risco,
        "risco_30d": risco_30d,
        "risco_60d": risco_60d,
        "risco_90d": risco_90d,
        "risco_120d": risco_120d,
        "risco_150d": risco_150d,
        "risco_180d": risco_180d,
    }

# Carregar dados
data = load_data()

# Header
st.title("📊 Dashboard de Devoluções BlueWorks")
st.markdown("Análise de vendas e devoluções - Últimos 180 dias")

# Sidebar para navegação
st.sidebar.title("Navegação")
page = st.sidebar.radio(
    "Selecione a visualização:",
    ["📈 Resumo Executivo", "🎯 Análise por Período", "📦 SKUs em Risco", 
     "🔍 Motivos de Devolução", "🚚 Canais de Entrega", "💰 Impacto Financeiro"]
)

# ==================== PÁGINA 1: RESUMO EXECUTIVO ====================
if page == "📈 Resumo Executivo":
    st.header("Resumo Executivo - 180 dias")
    
    # Dados do período de 180 dias
    resumo_180 = data["resumo"].iloc[-1]  # Última linha (180 dias)
    
    # KPIs principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total de Vendas",
            f"{int(resumo_180['vendas']):,}",
            f"R$ {resumo_180['faturamento_total_c_receita_envio']:,.2f}"
        )
    
    with col2:
        taxa_devol = resumo_180['taxa_devolucao_por_venda'] * 100
        st.metric(
            "Taxa de Devolução",
            f"{taxa_devol:.2f}%",
            f"{int(resumo_180['devolucoes_vendas'])} devoluções"
        )
    
    with col3:
        impacto = resumo_180['impacto_devolucao_ads']
        st.metric(
            "Impacto Financeiro",
            f"R$ {impacto:,.2f}",
            "Prejuízo com devoluções"
        )
    
    with col4:
        perda_total = resumo_180['perda_total_prod_frete_tarifa_aprox']
        st.metric(
            "Custo de Devolução",
            f"R$ {resumo_180['custo_devolucao_total']:,.2f}",
            "Custo total de devoluções"
        )
    
    st.divider()
    
    # Gráfico de tendência
    st.subheader("Tendência de Devoluções por Período")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data["resumo"]['janela_dias'],
        y=data["resumo"]['taxa_devolucao_por_venda'] * 100,
        mode='lines+markers',
        name='Taxa de Devolução (%)',
        line=dict(color='#FF6B6B', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Taxa de Devolução ao Longo do Período",
        xaxis_title="Dias",
        yaxis_title="Taxa (%)",
        hovermode='x unified',
        height=400,
        template="plotly_white"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Comparação: Saudável vs Crítica
    st.subheader("Classificação de Devoluções (180 dias)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_pie = go.Figure(data=[go.Pie(
            labels=data["saudavel_critica"]['classe'],
            values=data["saudavel_critica"]['devolucoes_vendas'],
            hole=0.3,
            marker=dict(colors=['#2ECC71', '#F39C12', '#E74C3C'])
        )])
        fig_pie.update_layout(
            title="Devoluções por Classe",
            height=400
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Tabela de detalhes
        st.dataframe(
            data["saudavel_critica"][['classe', 'devolucoes_vendas', 'impacto_devolucao', 'reembolsos']].style.format({
                'devolucoes_vendas': '{:,.0f}',
                'impacto_devolucao': 'R$ {:,.2f}',
                'reembolsos': 'R$ {:,.2f}'
            }),
            use_container_width=True,
            hide_index=True
        )

# ==================== PÁGINA 2: ANÁLISE POR PERÍODO ====================
elif page == "🎯 Análise por Período":
    st.header("Análise Comparativa por Período")
    
    resumo_df = data["resumo"].copy()
    
    # Seletor de período
    col1, col2 = st.columns(2)
    
    with col1:
        periodo_selecionado = st.selectbox(
            "Selecione o período (dias):",
            resumo_df['janela_dias'].values,
            index=len(resumo_df) - 1
        )
    
    dados_periodo = resumo_df[resumo_df['janela_dias'] == periodo_selecionado].iloc[0]
    
    # KPIs do período
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Vendas", f"{int(dados_periodo['vendas']):,}")
    with col2:
        st.metric("Unidades", f"{int(dados_periodo['unidades_vendidas']):,}")
    with col3:
        st.metric("Devoluções", f"{int(dados_periodo['devolucoes_vendas']):,}")
    with col4:
        st.metric("Taxa %", f"{dados_periodo['taxa_devolucao_por_venda']*100:.2f}%")
    
    st.divider()
    
    # Gráficos comparativos
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Vendas', 'Devoluções'],
            y=[dados_periodo['vendas'], dados_periodo['devolucoes_vendas']],
            marker_color=['#3498DB', '#E74C3C']
        ))
        fig.update_layout(
            title=f"Vendas vs Devoluções ({periodo_selecionado}d)",
            yaxis_title="Quantidade",
            height=400,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Faturamento', 'Impacto Devol.', 'Custo Devol.'],
            y=[
                dados_periodo['faturamento_total_c_receita_envio'],
                abs(dados_periodo['impacto_devolucao_ads']),
                dados_periodo['custo_devolucao_total']
            ],
            marker_color=['#2ECC71', '#F39C12', '#E74C3C']
        ))
        fig.update_layout(
            title=f"Impacto Financeiro ({periodo_selecionado}d)",
            yaxis_title="R$",
            height=400,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Tabela completa do período
    st.subheader("Detalhes Completos do Período")
    
    cols_display = ['janela_dias', 'vendas', 'unidades_vendidas', 'faturamento_total_c_receita_envio',
                   'devolucoes_vendas', 'taxa_devolucao_por_venda', 'impacto_devolucao_ads', 
                   'custo_devolucao_total']
    
    st.dataframe(
        resumo_df[cols_display].style.format({
            'faturamento_total_c_receita_envio': 'R$ {:,.2f}',
            'taxa_devolucao_por_venda': '{:.2%}',
            'impacto_devolucao_ads': 'R$ {:,.2f}',
            'custo_devolucao_total': 'R$ {:,.2f}'
        }),
        use_container_width=True,
        hide_index=True
    )

# ==================== PÁGINA 3: SKUS EM RISCO ====================
elif page == "📦 SKUs em Risco":
    st.header("SKUs em Risco Financeiro")
    
    # Seletor de período
    periodo = st.selectbox(
        "Período de análise:",
        ["30 dias", "60 dias", "90 dias", "120 dias", "150 dias", "180 dias"],
        index=5
    )
    
    periodo_map = {
        "30 dias": "risco_30d",
        "60 dias": "risco_60d",
        "90 dias": "risco_90d",
        "120 dias": "risco_120d",
        "150 dias": "risco_150d",
        "180 dias": "risco_180d"
    }
    
    df_risco = data[periodo_map[periodo]].copy()
    
    # Top 10 por risco
    top_risco = df_risco.nlargest(10, 'risco_financeiro_score')
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=top_risco['SKU'],
        x=top_risco['risco_financeiro_score'],
        orientation='h',
        marker_color='#E74C3C'
    ))
    fig.update_layout(
        title=f"Top 10 SKUs por Risco Financeiro ({periodo})",
        xaxis_title="Score de Risco",
        yaxis_title="SKU",
        height=500,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Tabela detalhada
    st.subheader("Detalhes dos SKUs em Risco")
    
    cols_risco = ['SKU', 'vendas', 'devolucoes_vendas', 'taxa_devolucao_venda', 
                  'impacto_devolucao', 'risco_financeiro_score']
    
    st.dataframe(
        top_risco[cols_risco].style.format({
            'taxa_devolucao_venda': '{:.2%}',
            'impacto_devolucao': 'R$ {:,.2f}',
            'risco_financeiro_score': '{:,.2f}'
        }),
        use_container_width=True,
        hide_index=True
    )

# ==================== PÁGINA 4: MOTIVOS DE DEVOLUÇÃO ====================
elif page == "🔍 Motivos de Devolução":
    st.header("Motivos de Devolução (180 dias)")
    
    motivos_df = data["motivos"].copy()
    motivos_df['pct_display'] = motivos_df['pct'] * 100
    
    # Gráfico de barras
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=motivos_df['Motivo'],
        y=motivos_df['pct_display'],
        marker_color='#3498DB',
        text=motivos_df['pct_display'].round(1),
        textposition='auto'
    ))
    fig.update_layout(
        title="Distribuição de Motivos de Devolução",
        xaxis_title="Motivo",
        yaxis_title="Percentual (%)",
        height=500,
        template="plotly_white",
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Tabela
    st.subheader("Detalhes dos Motivos")
    
    tabela_motivos = motivos_df.copy()
    tabela_motivos['pct'] = tabela_motivos['pct'] * 100
    tabela_motivos = tabela_motivos.rename(columns={'pct': 'Percentual (%)', 'devolucoes_vendas': 'Devoluções'})
    
    st.dataframe(
        tabela_motivos[['Motivo', 'Devoluções', 'Percentual (%)']].style.format({
            'Percentual (%)': '{:.2f}%'
        }),
        use_container_width=True,
        hide_index=True
    )

# ==================== PÁGINA 5: CANAIS DE ENTREGA ====================
elif page == "🚚 Canais de Entrega":
    st.header("Análise por Canal de Entrega (180 dias)")
    
    frete_df = data["frete"].copy()
    frete_df = frete_df[frete_df['Forma de entrega'].notna()]
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=frete_df['Forma de entrega'],
            y=frete_df['taxa_devolucao'],
            marker_color='#E74C3C'
        ))
        fig.update_layout(
            title="Taxa de Devolução por Canal",
            yaxis_title="Taxa (%)",
            height=400,
            template="plotly_white",
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=frete_df['Forma de entrega'],
            y=frete_df['devolucoes'],
            marker_color='#3498DB'
        ))
        fig.update_layout(
            title="Quantidade de Devoluções por Canal",
            yaxis_title="Devoluções",
            height=400,
            template="plotly_white",
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Tabela
    st.subheader("Detalhes por Canal")
    
    cols_frete = ['Forma de entrega', 'vendas', 'devolucoes', 'taxa_devolucao', 'custo_envio', 'impacto_devolucao']
    
    st.dataframe(
        frete_df[cols_frete].style.format({
            'taxa_devolucao': '{:.2%}',
            'custo_envio': 'R$ {:,.2f}',
            'impacto_devolucao': 'R$ {:,.2f}'
        }),
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    
    # Comparação: Full vs Matriz
    st.subheader("Comparação: Full vs Matriz (180 dias)")
    
    matriz_full_df = data["matriz_full"].copy()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure(data=[go.Pie(
            labels=matriz_full_df['Canal_devolucao'],
            values=matriz_full_df['devolucoes_vendas'],
            hole=0.3,
            marker=dict(colors=['#3498DB', '#E74C3C'])
        )])
        fig.update_layout(title="Devoluções por Canal", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.dataframe(
            matriz_full_df[['Canal_devolucao', 'devolucoes_vendas', 'taxa_devolucao', 'impacto_devolucao']].style.format({
                'taxa_devolucao': '{:.2%}',
                'impacto_devolucao': 'R$ {:,.2f}'
            }),
            use_container_width=True,
            hide_index=True
        )

# ==================== PÁGINA 6: IMPACTO FINANCEIRO ====================
elif page == "💰 Impacto Financeiro":
    st.header("Análise de Impacto Financeiro")
    
    st.subheader("Top 10 SKUs por Impacto Financeiro (180 dias)")
    
    top_perdas = data["top10_perdas"].copy()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=top_perdas['SKU'],
        x=top_perdas['impacto_devolucao'],
        orientation='h',
        marker_color='#E74C3C'
    ))
    fig.update_layout(
        title="Impacto Financeiro por SKU",
        xaxis_title="Impacto (R$)",
        yaxis_title="SKU",
        height=500,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    st.subheader("Top 10 SKUs por Taxa de Devolução (180 dias)")
    
    top_taxa = data["top10_taxa"].copy()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=top_taxa['SKU'],
        x=top_taxa['taxa_devolucao_venda'] * 100,
        orientation='h',
        marker_color='#F39C12'
    ))
    fig.update_layout(
        title="Taxa de Devolução por SKU",
        xaxis_title="Taxa (%)",
        yaxis_title="SKU",
        height=500,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    st.subheader("Detalhes Financeiros - Top 10 Maiores Perdas")
    
    cols_perdas = ['SKU', 'vendas', 'devolucoes_vendas', 'taxa_devolucao_venda', 
                   'impacto_devolucao', 'reembolsos', 'custo_devolucao']
    
    st.dataframe(
        top_perdas[cols_perdas].style.format({
            'taxa_devolucao_venda': '{:.2%}',
            'impacto_devolucao': 'R$ {:,.2f}',
            'reembolsos': 'R$ {:,.2f}',
            'custo_devolucao': 'R$ {:,.2f}'
        }),
        use_container_width=True,
        hide_index=True
    )

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.875rem; margin-top: 2rem;">
    <p>Dashboard de Devoluções BlueWorks | Dados: Últimos 180 dias | Atualizado em 27/02/2026</p>
</div>
""", unsafe_allow_html=True)
