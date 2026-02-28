import pandas as pd
from io import BytesIO
from utils.metricas import calcular_metricas, calcular_qualidade_arquivo

def exportar_xlsx(data):
    """Exporta os resultados para um arquivo XLSX corrigido"""
    
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
            'Faturamento Total (R$)',
            'Taxa de Devolução (%)',
            'Devoluções',
            'Impacto Financeiro (R$)',
            'Perda Total (R$)',
            'Perda Parcial (R$)',
            'Devoluções Saudáveis',
            'Devoluções Críticas',
            'Devoluções Neutras',
        ],
        'Valor': [
            metricas_180['vendas'],
            f"{metricas_180['faturamento_total']:.2f}",
            f"{metricas_180['taxa_devolucao'] * 100:.2f}",
            metricas_180['devolucoes_vendas'],
            f"{metricas_180['impacto_devolucao']:.2f}",
            f"{metricas_180['perda_total']:.2f}",
            f"{metricas_180['perda_parcial']:.2f}",
            metricas_180['saudaveis'],
            metricas_180['criticas'],
            metricas_180['neutras'],
        ]
    }
    
    pd.DataFrame(resumo_data).to_excel(writer, sheet_name='Resumo', index=False)
    
    # Aba 2: Qualidade (Corrigida para evitar KeyError)
    qualidade = calcular_qualidade_arquivo(data)
    qualidade_data = {
        'Métrica': [
            'SKU sem informação (%)',
            'Data sem informação (%)',
            'N.º de venda sem informação (%)',
            'Devoluções Matriz - Sem motivo (%)',
            'Devoluções Matriz - Sem estado (%)',
            'Devoluções Full - Sem motivo (%)',
            'Devoluções Full - Sem estado (%)',
        ],
        'Valor': [
            f"{qualidade['vendas']['sem_sku_pct']:.2f}",
            f"{qualidade['vendas']['sem_data_pct']:.2f}",
            f"{qualidade['vendas']['sem_numero_venda_pct']:.2f}",
            f"{qualidade['matriz']['sem_motivo_pct']:.2f}",
            f"{qualidade['matriz']['sem_estado_pct']:.2f}",
            f"{qualidade['full']['sem_motivo_pct']:.2f}",
            f"{qualidade['full']['sem_estado_pct']:.2f}",
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
            'Faturamento (R$)': f"{m['faturamento_total']:.2f}",
            'Devoluções': m['devolucoes_vendas'],
            'Taxa (%)': f"{m['taxa_devolucao'] * 100:.2f}",
            'Perda Total (R$)': f"{m['perda_total']:.2f}",
        })
    
    pd.DataFrame(janelas_data).to_excel(writer, sheet_name='Janelas', index=False)
    
    # Aba 4: Dados Brutos (limitados para performance)
    vendas.head(1000).to_excel(writer, sheet_name='Vendas_Brutos', index=False)
    pd.concat([matriz, full], ignore_index=True).head(1000).to_excel(writer, sheet_name='Devolucoes_Brutos', index=False)
    
    writer.close()
    output.seek(0)
    return output
