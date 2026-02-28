import pandas as pd
from io import BytesIO
from utils.metricas import calcular_metricas, calcular_qualidade_arquivo
from utils.formatacao import formatar_brl, formatar_pct_direto

def exportar_xlsx(data):
    """Exporta os resultados para um arquivo XLSX com formatação BRL padronizada"""
    
    vendas = data['vendas']
    matriz = data['matriz']
    full = data['full']
    max_date = data['max_date']
    
    if matriz is None: matriz = pd.DataFrame()
    if full is None: full = pd.DataFrame()
    
    # Criar writer
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    
    # Aba 1: Resumo
    metricas_180 = calcular_metricas(vendas, matriz, full, max_date, 180)
    
    resumo_data = {
        'Métrica': [
            'Total de Vendas',
            'Faturamento Produtos',
            'Faturamento Total',
            'Taxa de Devolução',
            'Devoluções',
            'Faturamento Devoluções',
            'Perda Total',
            'Perda Parcial',
            'Devoluções Saudáveis',
            'Devoluções Críticas',
            'Devoluções Neutras',
        ],
        'Valor': [
            metricas_180['vendas'],
            formatar_brl(metricas_180['faturamento_produtos']),
            formatar_brl(metricas_180['faturamento_total']),
            formatar_pct_direto(metricas_180['taxa_devolucao'] * 100),
            metricas_180['devolucoes_vendas'],
            formatar_brl(metricas_180['faturamento_devolucoes']),
            formatar_brl(metricas_180['perda_total']),
            formatar_brl(metricas_180['perda_parcial']),
            metricas_180['saudaveis'],
            metricas_180['criticas'],
            metricas_180['neutras'],
        ]
    }
    
    pd.DataFrame(resumo_data).to_excel(writer, sheet_name='Resumo', index=False)
    
    # Aba 2: Qualidade
    qualidade = calcular_qualidade_arquivo(data)
    qualidade_data = {
        'Métrica': [
            'SKU sem informação',
            'Data sem informação',
            'N.º de venda sem informação',
            'Devoluções Matriz - Sem motivo',
            'Devoluções Matriz - Sem estado',
            'Devoluções Full - Sem motivo',
            'Devoluções Full - Sem estado',
        ],
        'Valor': [
            formatar_pct_direto(qualidade['vendas']['sem_sku_pct']),
            formatar_pct_direto(qualidade['vendas']['sem_data_pct']),
            formatar_pct_direto(qualidade['vendas']['sem_numero_venda_pct']),
            formatar_pct_direto(qualidade['matriz']['sem_motivo_pct']),
            formatar_pct_direto(qualidade['matriz']['sem_estado_pct']),
            formatar_pct_direto(qualidade['full']['sem_motivo_pct']),
            formatar_pct_direto(qualidade['full']['sem_estado_pct']),
        ]
    }
    
    pd.DataFrame(qualidade_data).to_excel(writer, sheet_name='Qualidade', index=False)
    
    # Aba 3: Janelas
    janelas_data = []
    for janela in [30, 60, 90, 120, 150, 180]:
        m = calcular_metricas(vendas, matriz, full, max_date, janela)
        janelas_data.append({
            'Período (dias)': janela,
            'Vendas': m['vendas'],
            'Faturamento Prod.': formatar_brl(m['faturamento_produtos']),
            'Faturamento Total': formatar_brl(m['faturamento_total']),
            'Devoluções': m['devolucoes_vendas'],
            'Taxa': formatar_pct_direto(m['taxa_devolucao'] * 100),
            'Fat. Devoluções': formatar_brl(m['faturamento_devolucoes']),
            'Perda Total': formatar_brl(m['perda_total']),
            'Perda Parcial': formatar_brl(m['perda_parcial']),
        })
    
    pd.DataFrame(janelas_data).to_excel(writer, sheet_name='Janelas', index=False)
    
    # Aba 4: Dados Brutos (limitados para performance)
    vendas.head(1000).to_excel(writer, sheet_name='Vendas_Brutos', index=False)
    pd.concat([matriz, full], ignore_index=True).head(1000).to_excel(writer, sheet_name='Devolucoes_Brutos', index=False)
    
    writer.close()
    output.seek(0)
    return output
