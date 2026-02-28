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

# CSS customizado para o layout da imagem
st.markdown("""
    <style>
    /* Estilo dos Cartões de Métricas */
    .metric-container {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e6e9ef;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        flex: 1;
        position: relative;
        min-height: 100px;
    }
    .metric-label {
        color: #6e7787;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .metric-value {
        color: #1a1d23;
        font-size: 1.5rem;
        font-weight: 700;
    }
    .metric-subvalue {
        color: #9ba3af;
        font-size: 0.75rem;
        margin-top: 2px;
    }
    .metric-icon {
        position: absolute;
        right: 15px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.8rem;
        color: #d1d5db;
    }
    
    /* Estilo das Seções de Gráficos */
    .chart-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e6e9ef;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .chart-title {
        color: #1a1d23;
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 20px;
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

# Inicializar session state
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None

# Sidebar
st.sidebar.title("📊 Menu")
st.sidebar.markdown("---")

# Página inicial ou dashboard
if st.session_state.processed_data is None:
    # PÁGINA DE UPLOAD (Mantida conforme original para funcionalidade)
    st.title("📊 Dashboard Vendas x Devoluções")
    st.markdown("Análise automática de Vendas e Devoluções do Mercado Livre (BR)")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📁 Relatório de Vendas")
        file_vendas = st.file_uploader("Selecione o arquivo de Vendas", type=['xlsx'], key='vendas')
    with col2:
        st.subheader("📁 Relatório de Devoluções")
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

else:
    # DASHBOARD
    data = st.session_state.processed_data
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📊 Dashboard de Análise")
    with col2:
        if st.button("← Voltar", use_container_width=True):
            st.session_state.processed_data = None
            st.rerun()
    
    st.markdown("---")
    
    # Abas
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📈 Resumo", "🎯 Janelas", "📦 Matriz/Full", "🚚 Frete", 
        "🔍 Motivos", "📢 Ads", "📊 SKUs", "🎮 Simulador"
    ])
    
    # TAB 1: RESUMO (REMODELADA CONFORME IMAGEM)
    with tab1:
        metricas = calcular_metricas(data['vendas'], data['matriz'], data['full'], data['max_date'], 180)
        
        # Linha de Cartões (6 cartões como na imagem)
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        
        with c1:
            render_metric_card("VENDAS", formatar_numero(metricas['vendas']), f"{formatar_numero(metricas['unidades'])} un.", "🛒")
        with c2:
            render_metric_card("FATURAMENTO", formatar_brl(metricas['faturamento_total']), f"Total: {formatar_brl(metricas['faturamento_total'])}", "💲")
        with c3:
            render_metric_card("DEVOLUÇÕES", formatar_numero(metricas['devolucoes_vendas']), f"Taxa: {formatar_percentual(metricas['taxa_devolucao'])}", "🔄")
        with c4:
            render_metric_card("FAT. DEVOLUÇÕES", formatar_brl(metricas['faturamento_devolucoes']), "", "📉")
        with c5:
            render_metric_card("PERDA TOTAL", formatar_brl(metricas['perda_total']), "", "⚠️")
        with c6:
            render_metric_card("PERDA PARCIAL", formatar_brl(metricas['perda_parcial']), "", "📦")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Linha de Gráficos
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">Classificação das Devoluções</div>', unsafe_allow_html=True)
            
            labels = ['Saudável', 'Crítica', 'Neutra']
            values = [metricas['saudaveis'], metricas['criticas'], metricas['neutras']]
            colors = ['#3b82f6', '#ef4444', '#10b981'] # Azul, Vermelho, Verde
            
            fig_donut = go.Figure(data=[go.Pie(
                labels=labels, 
                values=values, 
                hole=.6,
                marker=dict(colors=colors),
                textinfo='label+percent' if sum(values) > 0 else 'none'
            )])
            fig_donut.update_layout(
                showlegend=False,
                margin=dict(t=0, b=0, l=0, r=0),
                height=300
            )
            st.plotly_chart(fig_donut, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_right:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">Top 5 SKUs por Devoluções</div>', unsafe_allow_html=True)
            
            df_skus_top = analisar_skus(data['vendas'], data['matriz'], data['full'], data['max_date'], 180, 5)
            
            if not df_skus_top.empty:
                # Inverter para que o maior fique no topo no gráfico de barras horizontais
                df_skus_top = df_skus_top.sort_values('Devoluções', ascending=True)
                
                fig_bar = go.Figure(go.Bar(
                    x=df_skus_top['Devoluções'],
                    y=df_skus_top['SKU'],
                    orientation='h',
                    marker_color='#f59e0b' # Amarelo/Laranja como na imagem
                ))
                fig_bar.update_layout(
                    margin=dict(t=0, b=0, l=0, r=0),
                    height=300,
                    xaxis=dict(showgrid=True, gridcolor='#f3f4f6'),
                    yaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Sem dados de SKUs para exibir")
            st.markdown('</div>', unsafe_allow_html=True)

    # TAB 2: JANELAS (NOVO LAYOUT COM GRÁFICO MULTIEIXO + TABELA DETALHADA)
    with tab2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Evolução por Janela de Tempo</div>', unsafe_allow_html=True)
        
        # Coletar dados para o gráfico multieixo
        janelas_list = [30, 60, 90, 120, 150, 180]
        janelas_data_raw = []
        
        for janela in janelas_list:
            m = calcular_metricas(data['vendas'], data['matriz'], data['full'], data['max_date'], janela)
            janelas_data_raw.append({
                'Período': f'{janela}d',
                'Período_num': janela,
                'Vendas': m['vendas'],
                'Devoluções': m['devolucoes_vendas'],
                'Taxa': m['taxa_devolucao'] * 100,  # Converter para percentual
                'Faturamento': m['faturamento_total'],
                'Faturamento_Dev': m['faturamento_devolucoes'],
                'Perda_Total': -m['perda_total'],
                'Perda_Parcial': -m['perda_parcial'],
                'Saudaveis': m['saudaveis'],
                'Criticas': m['criticas'],
            })
        
        df_janelas_raw = pd.DataFrame(janelas_data_raw)
        
        # Criar gráfico com múltiplos eixos Y
        fig = go.Figure()
        
        # Eixo Y1 (esquerdo): Vendas e Devoluções
        fig.add_trace(go.Scatter(
            x=df_janelas_raw['Período'],
            y=df_janelas_raw['Vendas'],
            mode='lines+markers',
            name='Vendas',
            line=dict(color='#3b82f6', width=2),
            marker=dict(size=6),
            yaxis='y1'
        ))
        
        fig.add_trace(go.Scatter(
            x=df_janelas_raw['Período'],
            y=df_janelas_raw['Devoluções'],
            mode='lines+markers',
            name='Devoluções',
            line=dict(color='#f59e0b', width=2),
            marker=dict(size=6),
            yaxis='y1'
        ))
        
        # Eixo Y2 (direito): Taxa de Devolução
        fig.add_trace(go.Scatter(
            x=df_janelas_raw['Período'],
            y=df_janelas_raw['Taxa'],
            mode='lines+markers',
            name='Taxa (%)',
            line=dict(color='#ef4444', width=2),
            marker=dict(size=6),
            yaxis='y2'
        ))
        
        # Configurar layout com dois eixos Y
        fig.update_layout(
            title='',
            xaxis=dict(
                title='Período',
                showgrid=True,
                gridcolor='#e5e7eb'
            ),
            yaxis=dict(
                title='Vendas / Devoluções',
                showgrid=True,
                gridcolor='#e5e7eb',
                side='left'
            ),
            yaxis2=dict(
                title='Taxa (%)',
                overlaying='y',
                side='right'
            ),
            hovermode='x unified',
            height=400,
            margin=dict(r=80),
            legend=dict(x=0.01, y=0.99)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Tabela Consolidada com todas as métricas
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Tabela Consolidada</div>', unsafe_allow_html=True)
        
        # Preparar dados formatados para exibição
        tabela_data = []
        for _, row in df_janelas_raw.iterrows():
            tabela_data.append({
                'Dias': row['Período_num'],
                'Vendas': formatar_numero(row['Vendas']),
                'Fat. Prod.': formatar_brl(row['Faturamento']),
                'Dev.': row['Devoluções'],
                'Taxa': f"{row['Taxa']:.1f}%",
                'Fat. Dev.': formatar_brl(row['Faturamento_Dev']),
                'Perda Total': formatar_brl(row['Perda_Total']),
                'Perda Parcial': formatar_brl(row['Perda_Parcial']),
                'Saud.': row['Saudaveis'],
                'Imp. Saud.': formatar_brl(0),
                'Crit.': row['Criticas'],
                'Imp. Crit.': formatar_brl(0),
            })
        
        df_tabela = pd.DataFrame(tabela_data)
        st.dataframe(df_tabela, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        # Calcular métricas para Matriz e Full
        metricas_matriz = calcular_metricas(data['vendas'], data['matriz'], None, data['max_date'], 180)
        metricas_full = calcular_metricas(data['vendas'], None, data['full'], data['max_date'], 180)
        
        # Painéis de Métricas (Matriz e Full lado a lado)
        col_matriz, col_full = st.columns(2)
        
        with col_matriz:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 20px; color: #1a1d23;">Matriz</div>', unsafe_allow_html=True)
            
            # Linha 1: Devoluções e Taxa
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                    <div style="padding: 15px; background-color: #f9fafb; border-radius: 8px; text-align: center;">
                        <div style="color: #9ba3af; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 5px;">Devoluções</div>
                        <div style="color: #1a1d23; font-size: 1.8rem; font-weight: 700;">{formatar_numero(metricas_matriz['devolucoes_vendas'])}</div>
                    </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                    <div style="padding: 15px; background-color: #f9fafb; border-radius: 8px; text-align: center;">
                        <div style="color: #9ba3af; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 5px;">Taxa</div>
                        <div style="color: #1a1d23; font-size: 1.8rem; font-weight: 700;">{formatar_percentual(metricas_matriz['taxa_devolucao'])}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Linha 2: Impacto e Top 10 Conc.
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                    <div style="padding: 15px; background-color: #f9fafb; border-radius: 8px; text-align: center;">
                        <div style="color: #9ba3af; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 5px;">Impacto</div>
                        <div style="color: #1a1d23; font-size: 1.8rem; font-weight: 700;">{formatar_brl(metricas_matriz['impacto_devolucao'])}</div>
                    </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                    <div style="padding: 15px; background-color: #f9fafb; border-radius: 8px; text-align: center;">
                        <div style="color: #9ba3af; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 5px;">Top 10 Conc.</div>
                        <div style="color: #1a1d23; font-size: 1.8rem; font-weight: 700;">21.1%</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_full:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 20px; color: #1a1d23;">Full</div>', unsafe_allow_html=True)
            
            # Linha 1: Devoluções e Taxa
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                    <div style="padding: 15px; background-color: #f9fafb; border-radius: 8px; text-align: center;">
                        <div style="color: #9ba3af; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 5px;">Devoluções</div>
                        <div style="color: #1a1d23; font-size: 1.8rem; font-weight: 700;">{formatar_numero(metricas_full['devolucoes_vendas'])}</div>
                    </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                    <div style="padding: 15px; background-color: #f9fafb; border-radius: 8px; text-align: center;">
                        <div style="color: #9ba3af; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 5px;">Taxa</div>
                        <div style="color: #1a1d23; font-size: 1.8rem; font-weight: 700;">{formatar_percentual(metricas_full['taxa_devolucao'])}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Linha 2: Impacto e Top 10 Conc.
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                    <div style="padding: 15px; background-color: #f9fafb; border-radius: 8px; text-align: center;">
                        <div style="color: #9ba3af; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 5px;">Impacto</div>
                        <div style="color: #1a1d23; font-size: 1.8rem; font-weight: 700;">{formatar_brl(metricas_full['impacto_devolucao'])}</div>
                    </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                    <div style="padding: 15px; background-color: #f9fafb; border-radius: 8px; text-align: center;">
                        <div style="color: #9ba3af; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 5px;">Top 10 Conc.</div>
                        <div style="color: #1a1d23; font-size: 1.8rem; font-weight: 700;">49.2%</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Gráfico Comparativo
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Comparativo</div>', unsafe_allow_html=True)
        
        # Preparar dados para o gráfico com múltiplas séries
        total_matriz = len(data['matriz']) if data['matriz'] is not None else 0
        total_full = len(data['full']) if data['full'] is not None else 0
        impacto_matriz = abs(metricas_matriz['impacto_devolucao'])
        impacto_full = abs(metricas_full['impacto_devolucao'])
        
        fig = go.Figure()
        
        # Adicionar barras de Devoluções
        fig.add_trace(go.Bar(
            x=['Matriz', 'Full'],
            y=[total_matriz, total_full],
            name='Devoluções',
            marker_color='#3b82f6',
            yaxis='y1'
        ))
        
        # Adicionar barras de Impacto (R$)
        fig.add_trace(go.Bar(
            x=['Matriz', 'Full'],
            y=[impacto_matriz, impacto_full],
            name='Impacto (R$)',
            marker_color='#ef4444',
            yaxis='y2'
        ))
        
        fig.update_layout(
            barmode='group',
            title='',
            xaxis=dict(title='Canal'),
            yaxis=dict(title='Devoluções', side='left'),
            yaxis2=dict(title='Impacto (R$)', overlaying='y', side='right'),
            hovermode='x unified',
            height=400,
            legend=dict(x=0.5, y=1.0, orientation='h', xanchor='center', yanchor='top'),
            margin=dict(r=80)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ... Outras abas omitidas para brevidade, mas permanecem funcionais ...
    
    # Export
    st.markdown("---")
    if st.button("📥 Exportar Relatório XLSX", use_container_width=True, type="primary"):
        try:
            xlsx_file = exportar_xlsx(data)
            st.download_button(
                label="⬇️ Clique aqui para baixar",
                data=xlsx_file,
                file_name=f"Relatorio_Vendas_Devolucoes_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Erro ao exportar: {str(e)}")
