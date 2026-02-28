import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.formatacao import formatar_brl, formatar_percentual, formatar_numero

def analisar_frete(vendas, matriz, full, max_date, dias_atras):
    """Análise de frete e forma de entrega"""
    
    if matriz is None:
        matriz = pd.DataFrame()
    if full is None:
        full = pd.DataFrame()
    
    data_limite = max_date - timedelta(days=dias_atras)
    
    if 'Data da venda' in vendas.columns:
        vendas_periodo = vendas[vendas['Data da venda'] >= data_limite].copy()
    else:
        vendas_periodo = vendas.copy()
    
    # Criar mapa de devoluções
    todas_dev = pd.concat([matriz, full], ignore_index=True)
    dev_map = {}
    
    if len(todas_dev) > 0 and 'N.º de venda' in todas_dev.columns:
        for _, row in todas_dev.iterrows():
            num_venda = str(row['N.º de venda'])
            if num_venda not in dev_map:
                dev_map[num_venda] = []
            dev_map[num_venda].append(row)
    
    # Análise por forma de entrega
    frete_data = []
    
    if 'Forma de entrega' in vendas_periodo.columns:
        formas = vendas_periodo['Forma de entrega'].dropna().unique()
        
        for forma in formas:
            vendas_forma = vendas_periodo[vendas_periodo['Forma de entrega'] == forma]
            total_vendas = len(vendas_forma)
            
            # Contar devoluções
            dev_count = 0
            dev_valor = 0
            
            for _, venda in vendas_forma.iterrows():
                num_venda = str(venda.get('N.º de venda', ''))
                if num_venda in dev_map:
                    dev_count += len(dev_map[num_venda])
                    for dev in dev_map[num_venda]:
                        reembolso = dev.get('Receita por produtos (BRL)', 0) or 0
                        if pd.isna(reembolso):
                            reembolso = 0
                        dev_valor += reembolso
            
            taxa = (dev_count / total_vendas * 100) if total_vendas > 0 else 0
            
            frete_data.append({
                'Forma de Entrega': forma,
                'Vendas': total_vendas,
                'Devoluções': dev_count,
                'Taxa (%)': taxa,
                'Impacto (R$)': -dev_valor,
            })
    
    df = pd.DataFrame(frete_data) if frete_data else pd.DataFrame()
    if len(df) > 0:
        df['Vendas'] = df['Vendas'].apply(formatar_numero)
        df['Devoluções'] = df['Devoluções'].apply(formatar_numero)
        df['Taxa (%)'] = df['Taxa (%)'].apply(lambda x: formatar_percentual(x/100))
        df['Impacto (R$)'] = df['Impacto (R$)'].apply(formatar_brl)
    return df

def analisar_motivos(matriz, full, max_date, dias_atras):
    """Análise de motivos de devolução"""
    
    if matriz is None:
        matriz = pd.DataFrame()
    if full is None:
        full = pd.DataFrame()
    
    data_limite = max_date - timedelta(days=dias_atras)
    
    todas_dev = pd.concat([matriz, full], ignore_index=True)
    
    if 'Data da venda' in todas_dev.columns:
        todas_dev = todas_dev[todas_dev['Data da venda'] >= data_limite].copy()
    
    motivos_data = []
    
    if 'Motivo do resultado' in todas_dev.columns:
        motivos = todas_dev['Motivo do resultado'].dropna().value_counts()
        
        for motivo, count in motivos.items():
            motivos_data.append({
                'Motivo': str(motivo)[:50],  # Limitar tamanho
                'Quantidade': count,
                'Percentual (%)': (count / len(todas_dev) * 100) if len(todas_dev) > 0 else 0,
            })
    
    df = pd.DataFrame(motivos_data) if motivos_data else pd.DataFrame()
    if len(df) > 0:
        df['Quantidade'] = df['Quantidade'].apply(formatar_numero)
        df['Percentual (%)'] = df['Percentual (%)'].apply(lambda x: formatar_percentual(x/100))
    return df

def analisar_ads(vendas, matriz, full, max_date, dias_atras):
    """Análise de vendas por publicidade (Ads)"""
    
    if matriz is None:
        matriz = pd.DataFrame()
    if full is None:
        full = pd.DataFrame()
    
    data_limite = max_date - timedelta(days=dias_atras)
    
    if 'Data da venda' in vendas.columns:
        vendas_periodo = vendas[vendas['Data da venda'] >= data_limite].copy()
    else:
        vendas_periodo = vendas.copy()
    
    # Criar mapa de devoluções
    todas_dev = pd.concat([matriz, full], ignore_index=True)
    dev_map = {}
    
    if len(todas_dev) > 0 and 'N.º de venda' in todas_dev.columns:
        for _, row in todas_dev.iterrows():
            num_venda = str(row['N.º de venda'])
            if num_venda not in dev_map:
                dev_map[num_venda] = []
            dev_map[num_venda].append(row)
    
    # Análise por publicidade
    ads_data = []
    
    if 'Venda por publicidade' in vendas_periodo.columns:
        # Agrupar por sim/não
        for pub_type in ['Sim', 'Não']:
            vendas_pub = vendas_periodo[vendas_periodo['Venda por publicidade'] == pub_type]
            total_vendas = len(vendas_pub)
            
            if total_vendas == 0:
                continue
            
            # Contar devoluções
            dev_count = 0
            receita_total = 0
            receita_dev = 0
            
            for _, venda in vendas_pub.iterrows():
                receita = venda.get('Receita por produtos (BRL)', 0) or 0
                if pd.isna(receita):
                    receita = 0
                receita_total += receita
                
                num_venda = str(venda.get('N.º de venda', ''))
                if num_venda in dev_map:
                    dev_count += len(dev_map[num_venda])
                    for dev in dev_map[num_venda]:
                        reembolso = dev.get('Receita por produtos (BRL)', 0) or 0
                        if pd.isna(reembolso):
                            reembolso = 0
                        receita_dev += reembolso
            
            taxa = (dev_count / total_vendas * 100) if total_vendas > 0 else 0
            
            ads_data.append({
                'Tipo': f'Com Publicidade' if pub_type == 'Sim' else 'Sem Publicidade',
                'Vendas': total_vendas,
                'Devoluções': dev_count,
                'Taxa (%)': taxa,
                'Receita (R$)': receita_total,
                'Impacto (R$)': -receita_dev,
            })
    
    df = pd.DataFrame(ads_data) if ads_data else pd.DataFrame()
    if len(df) > 0:
        df['Vendas'] = df['Vendas'].apply(formatar_numero)
        df['Devoluções'] = df['Devoluções'].apply(formatar_numero)
        df['Taxa (%)'] = df['Taxa (%)'].apply(lambda x: formatar_percentual(x/100))
        df['Receita (R$)'] = df['Receita (R$)'].apply(formatar_brl)
        df['Impacto (R$)'] = df['Impacto (R$)'].apply(formatar_brl)
    return df

def analisar_skus(vendas, matriz, full, max_date, dias_atras, top_n=10):
    """Análise de SKUs com maior risco"""
    
    if matriz is None:
        matriz = pd.DataFrame()
    if full is None:
        full = pd.DataFrame()
    
    data_limite = max_date - timedelta(days=dias_atras)
    
    if 'Data da venda' in vendas.columns:
        vendas_periodo = vendas[vendas['Data da venda'] >= data_limite].copy()
    else:
        vendas_periodo = vendas.copy()
    
    # Criar mapa de devoluções
    todas_dev = pd.concat([matriz, full], ignore_index=True)
    dev_map = {}
    
    if len(todas_dev) > 0 and 'N.º de venda' in todas_dev.columns:
        for _, row in todas_dev.iterrows():
            num_venda = str(row['N.º de venda'])
            if num_venda not in dev_map:
                dev_map[num_venda] = []
            dev_map[num_venda].append(row)
    
    # Análise por SKU
    skus_data = {}
    
    if 'SKU' in vendas_periodo.columns:
        for _, venda in vendas_periodo.iterrows():
            sku = str(venda.get('SKU', 'N/A'))
            
            if sku not in skus_data:
                skus_data[sku] = {
                    'vendas': 0,
                    'devolucoes': 0,
                    'receita': 0,
                    'impacto': 0,
                }
            
            skus_data[sku]['vendas'] += 1
            
            receita = venda.get('Receita por produtos (BRL)', 0) or 0
            if pd.isna(receita):
                receita = 0
            skus_data[sku]['receita'] += receita
            
            num_venda = str(venda.get('N.º de venda', ''))
            if num_venda in dev_map:
                skus_data[sku]['devolucoes'] += len(dev_map[num_venda])
                for dev in dev_map[num_venda]:
                    reembolso = dev.get('Receita por produtos (BRL)', 0) or 0
                    if pd.isna(reembolso):
                        reembolso = 0
                    skus_data[sku]['impacto'] += reembolso
    
    # Converter para DataFrame e calcular taxa
    skus_list = []
    for sku, data in skus_data.items():
        taxa = (data['devolucoes'] / data['vendas'] * 100) if data['vendas'] > 0 else 0
        score_risco = taxa * data['impacto'] / 100 if data['impacto'] > 0 else 0
        
        skus_list.append({
            'SKU': sku,
            'Vendas': data['vendas'],
            'Devoluções': data['devolucoes'],
            'Taxa (%)': taxa,
            'Receita (R$)': data['receita'],
            'Impacto (R$)': -data['impacto'],
            'Score Risco': score_risco,
        })
    
    df_skus = pd.DataFrame(skus_list)
    
    if len(df_skus) > 0:
        df_skus = df_skus.sort_values('Score Risco', ascending=False).head(top_n)
        df_skus['Vendas'] = df_skus['Vendas'].apply(formatar_numero)
        df_skus['Devoluções'] = df_skus['Devoluções'].apply(formatar_numero)
        df_skus['Taxa (%)'] = df_skus['Taxa (%)'].apply(lambda x: formatar_percentual(x/100))
        df_skus['Receita (R$)'] = df_skus['Receita (R$)'].apply(formatar_brl)
        df_skus['Impacto (R$)'] = df_skus['Impacto (R$)'].apply(formatar_brl)
    
    return df_skus

def simular_reducao(vendas, matriz, full, max_date, dias_atras, reducao_percentual):
    """Simula o impacto de redução na taxa de devolução"""
    
    if matriz is None:
        matriz = pd.DataFrame()
    if full is None:
        full = pd.DataFrame()
    
    data_limite = max_date - timedelta(days=dias_atras)
    
    if 'Data da venda' in vendas.columns:
        vendas_periodo = vendas[vendas['Data da venda'] >= data_limite].copy()
    else:
        vendas_periodo = vendas.copy()
    
    # Criar mapa de devoluções
    todas_dev = pd.concat([matriz, full], ignore_index=True)
    dev_map = {}
    
    if len(todas_dev) > 0 and 'N.º de venda' in todas_dev.columns:
        for _, row in todas_dev.iterrows():
            num_venda = str(row['N.º de venda'])
            if num_venda not in dev_map:
                dev_map[num_venda] = []
            dev_map[num_venda].append(row)
    
    # Calcular cenários
    vendas_totais = len(vendas_periodo)
    faturamento_total = vendas_periodo['Receita por produtos (BRL)'].sum() if 'Receita por produtos (BRL)' in vendas_periodo.columns else 0
    
    # Cenário atual
    devolucoes_atuais = 0
    impacto_atual = 0
    
    for _, venda in vendas_periodo.iterrows():
        num_venda = str(venda.get('N.º de venda', ''))
        if num_venda in dev_map:
            devolucoes_atuais += len(dev_map[num_venda])
            for dev in dev_map[num_venda]:
                reembolso = dev.get('Receita por produtos (BRL)', 0) or 0
                if pd.isna(reembolso):
                    reembolso = 0
                impacto_atual += reembolso
    
    taxa_atual = (devolucoes_atuais / vendas_totais * 100) if vendas_totais > 0 else 0
    
    # Cenário simulado
    devolucoes_simuladas = int(devolucoes_atuais * (1 - reducao_percentual / 100))
    impacto_simulado = impacto_atual * (1 - reducao_percentual / 100)
    taxa_simulada = (devolucoes_simuladas / vendas_totais * 100) if vendas_totais > 0 else 0
    
    economia = impacto_atual - impacto_simulado
    
    return {
        'vendas_totais': vendas_totais,
        'faturamento_total': faturamento_total,
        'cenario_atual': {
            'devolucoes': devolucoes_atuais,
            'taxa': taxa_atual,
            'impacto': -impacto_atual,
        },
        'cenario_simulado': {
            'devolucoes': devolucoes_simuladas,
            'taxa': taxa_simulada,
            'impacto': -impacto_simulado,
        },
        'economia': economia,
        'reducao_percentual': reducao_percentual,
    }
