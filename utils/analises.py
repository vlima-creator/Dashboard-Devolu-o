import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def analisar_frete(vendas, matriz, full, max_date, dias_atras):
    """
    Análise de frete e forma de entrega.
    Os dados já chegam filtrados pelo cabeçalho global.
    """
    
    if matriz is None:
        matriz = pd.DataFrame()
    if full is None:
        full = pd.DataFrame()
    
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
        # Preencher valores vazios com 'Mercado Envios' (identificado nos relatórios reais)
        vendas_periodo['Forma de entrega'] = vendas_periodo['Forma de entrega'].fillna('Mercado Envios').replace(['', ' '], 'Mercado Envios')
        formas = vendas_periodo['Forma de entrega'].unique()
        
        for forma in formas:
            vendas_forma = vendas_periodo[vendas_periodo['Forma de entrega'] == forma]
            total_vendas = len(vendas_forma)
            
            dev_count = 0
            dev_valor = 0.0
            
            vendas_devolvidas = set()
            for _, venda in vendas_forma.iterrows():
                num_venda = str(venda.get('N.º de venda', ''))
                if num_venda in dev_map and num_venda not in vendas_devolvidas:
                    vendas_devolvidas.add(num_venda)
                    dev_count += 1
                    for dev in dev_map[num_venda]:
                        # Usar Cancelamentos e reembolsos para impacto real
                        reembolso = dev.get('Cancelamentos e reembolsos (BRL)', None)
                        if reembolso is None or pd.isna(reembolso):
                            reembolso = 0.0
                        reembolso = float(reembolso)
                        if reembolso == 0:
                            fallback = dev.get('Receita por produtos (BRL)', 0)
                            if pd.isna(fallback): fallback = 0.0
                            reembolso = float(fallback)
                        dev_valor += reembolso
            
            taxa = (dev_count / total_vendas * 100) if total_vendas > 0 else 0
            
            frete_data.append({
                'Forma de Entrega': forma,
                'Vendas': total_vendas,
                'Devoluções': dev_count,
                'Taxa (%)': round(taxa, 1),
                'Impacto (R$)': round(-dev_valor, 2),
            })
    
    return pd.DataFrame(frete_data) if frete_data else pd.DataFrame()

def analisar_motivos(matriz, full, max_date, dias_atras):
    """
    Análise de motivos de devolução.
    Os dados já chegam filtrados pelo cabeçalho global.
    """
    
    if matriz is None:
        matriz = pd.DataFrame()
    if full is None:
        full = pd.DataFrame()
    
    todas_dev = pd.concat([matriz, full], ignore_index=True)
    
    motivos_data = []
    
    if len(todas_dev) > 0 and 'Motivo do resultado' in todas_dev.columns:
        def categorizar_vazio(row):
            motivo = str(row['Motivo do resultado']).strip()
            if motivo != '' and motivo != 'nan':
                return motivo
            
            estado = str(row.get('Estado', '')).lower()
            status = str(row.get('Descrição do status', '')).lower()
            
            if 'te demos o dinheiro' in estado or 'te demos o dinheiro' in status:
                return 'Reembolso ao Vendedor'
            if 'reembolso' in estado or 'reembolsamos' in status:
                return 'Reembolso ao Comprador'
            if 'mediação' in estado or 'mediação' in status:
                return 'Finalizado via Mediação'
            if 'cancelada' in estado or 'cancelada' in status:
                return 'Venda Cancelada'
            if 'não entregue' in estado or 'não foi feita' in estado:
                return 'Devolução não realizada'
            if 'enviamos de volta' in estado or 'devolvemos o produto ao comprador' in estado:
                return 'Produto devolvido ao comprador'
            if 'devolvido' in estado or 'devolução finalizada' in estado:
                return 'Devolução Concluída'
            
            return 'Outros Motivos de Devolução'

        # Aplicar categorização inteligente para motivos vazios
        todas_dev['Motivo do resultado'] = todas_dev.apply(categorizar_vazio, axis=1)
        
        motivos = todas_dev['Motivo do resultado'].value_counts()
        total_com_motivo = motivos.sum()
        
        for motivo, count in motivos.items():
            motivos_data.append({
                'Motivo': str(motivo)[:50],
                'Quantidade': int(count),
                'Percentual (%)': round((count / total_com_motivo * 100), 1) if total_com_motivo > 0 else 0,
            })
    
    return pd.DataFrame(motivos_data) if motivos_data else pd.DataFrame()

def analisar_ads(vendas, matriz, full, max_date, dias_atras):
    """
    Análise de vendas por publicidade (Ads).
    Os dados já chegam filtrados pelo cabeçalho global.
    """
    
    if matriz is None:
        matriz = pd.DataFrame()
    if full is None:
        full = pd.DataFrame()
    
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
        # Processar Ads (Sim)
        vendas_pub = vendas_periodo[vendas_periodo['Venda por publicidade'] == 'Sim']
        total_vendas = len(vendas_pub)
        
        if total_vendas > 0:
            dev_count = 0
            receita_total = 0.0
            impacto_total = 0.0
            
            vendas_devolvidas = set()
            for _, venda in vendas_pub.iterrows():
                receita = venda.get('Receita por produtos (BRL)', 0)
                if pd.isna(receita): receita = 0.0
                receita_total += float(receita)
                
                num_venda = str(venda.get('N.º de venda', ''))
                if num_venda in dev_map and num_venda not in vendas_devolvidas:
                    vendas_devolvidas.add(num_venda)
                    dev_count += 1
                    for dev in dev_map[num_venda]:
                        # Usar Cancelamentos e reembolsos para impacto real
                        reembolso = dev.get('Cancelamentos e reembolsos (BRL)', None)
                        if reembolso is None or pd.isna(reembolso):
                            reembolso = 0.0
                        reembolso = float(reembolso)
                        if reembolso == 0:
                            fallback = dev.get('Receita por produtos (BRL)', 0)
                            if pd.isna(fallback): fallback = 0.0
                            reembolso = float(fallback)
                        impacto_total += reembolso
            
            taxa = (dev_count / total_vendas * 100) if total_vendas > 0 else 0
            
            ads_data.append({
                'Tipo': 'Com Publicidade',
                'Vendas': total_vendas,
                'Devoluções': dev_count,
                'Taxa (%)': round(taxa, 1),
                'Receita (R$)': round(receita_total, 2),
                'Impacto (R$)': round(-impacto_total, 2),
            })
        
        # Processar Orgânico (vazio ou não 'Sim')
        vendas_pub = vendas_periodo[vendas_periodo['Venda por publicidade'] != 'Sim']
        total_vendas = len(vendas_pub)
        
        if total_vendas > 0:
            
            dev_count = 0
            receita_total = 0.0
            impacto_total = 0.0
            
            vendas_devolvidas = set()
            for _, venda in vendas_pub.iterrows():
                receita = venda.get('Receita por produtos (BRL)', 0)
                if pd.isna(receita): receita = 0.0
                receita_total += float(receita)
                
                num_venda = str(venda.get('N.º de venda', ''))
                if num_venda in dev_map and num_venda not in vendas_devolvidas:
                    vendas_devolvidas.add(num_venda)
                    dev_count += 1
                    for dev in dev_map[num_venda]:
                        # Usar Cancelamentos e reembolsos para impacto real
                        reembolso = dev.get('Cancelamentos e reembolsos (BRL)', None)
                        if reembolso is None or pd.isna(reembolso):
                            reembolso = 0.0
                        reembolso = float(reembolso)
                        if reembolso == 0:
                            fallback = dev.get('Receita por produtos (BRL)', 0)
                            if pd.isna(fallback): fallback = 0.0
                            reembolso = float(fallback)
                        impacto_total += reembolso
            
            taxa = (dev_count / total_vendas * 100) if total_vendas > 0 else 0
            
            ads_data.append({
                'Tipo': 'Orgânico',
                'Vendas': total_vendas,
                'Devoluções': dev_count,
                'Taxa (%)': round(taxa, 1),
                'Receita (R$)': round(receita_total, 2),
                'Impacto (R$)': round(-impacto_total, 2),
            })
    
    return pd.DataFrame(ads_data) if ads_data else pd.DataFrame()

def analisar_skus(vendas, matriz, full, max_date, dias_atras, top_n=None):
    """
    Análise de SKUs com maior risco.
    Os dados já chegam filtrados pelo cabeçalho global.
    """
    
    if matriz is None:
        matriz = pd.DataFrame()
    if full is None:
        full = pd.DataFrame()
    
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
            if pd.isna(venda.get('SKU')):
                sku = 'N/A'
            
            if sku not in skus_data:
                skus_data[sku] = {
                    'vendas': 0,
                    'devolucoes': 0,
                    'receita': 0.0,
                    'impacto': 0.0,
                    'reembolso': 0.0,
                    'custo_dev': 0.0,
                    'vendas_devolvidas': set(),
                }
            
            skus_data[sku]['vendas'] += 1
            
            receita = venda.get('Receita por produtos (BRL)', 0)
            if pd.isna(receita): receita = 0.0
            skus_data[sku]['receita'] += float(receita)
            
            num_venda = str(venda.get('N.º de venda', ''))
            if num_venda in dev_map and num_venda not in skus_data[sku]['vendas_devolvidas']:
                skus_data[sku]['vendas_devolvidas'].add(num_venda)
                skus_data[sku]['devolucoes'] += 1
                
                for dev in dev_map[num_venda]:
                    # Impacto: Cancelamentos e reembolsos
                    reemb = dev.get('Cancelamentos e reembolsos (BRL)', None)
                    if reemb is None or pd.isna(reemb):
                        reemb = 0.0
                    reemb = float(reemb)
                    if reemb == 0:
                        fallback = dev.get('Receita por produtos (BRL)', 0)
                        if pd.isna(fallback): fallback = 0.0
                        reemb = float(fallback)
                    skus_data[sku]['impacto'] += reemb
                    skus_data[sku]['reembolso'] += reemb
                    
                    # Custo de devolução (custos de envio)
                    custo = dev.get('Custos de envio (BRL)', None)
                    if custo is None or pd.isna(custo):
                        custo = 0.0
                    skus_data[sku]['custo_dev'] += float(custo)
    
    # Calcular total de devoluções para concentração
    total_devolucoes = sum(d['devolucoes'] for d in skus_data.values())
    
    # Converter para DataFrame
    skus_list = []
    for sku, d in skus_data.items():
        if d['devolucoes'] == 0:
            continue
        
        taxa = (d['devolucoes'] / d['vendas'] * 100) if d['vendas'] > 0 else 0
        score_risco = taxa * d['impacto'] / 100 if d['impacto'] > 0 else 0
        
        # Classificação
        if taxa >= 15:
            classe = 'Crítica'
        elif taxa >= 8:
            classe = 'Atenção'
        else:
            classe = 'Neutra'
        
        skus_list.append({
            'SKU': sku,
            'Vendas': d['vendas'],
            'Dev.': d['devolucoes'],
            'Taxa': round(taxa, 1),
            'Impacto': round(-d['impacto'], 2),
            'Reemb.': round(-abs(d['reembolso']), 2),
            'Custo Dev.': round(-abs(d['custo_dev']), 2),
            'Risco': round(score_risco, 3),
            'Classe': classe,
        })
    
    df_skus = pd.DataFrame(skus_list)
    
    if len(df_skus) > 0:
        df_skus = df_skus.sort_values('Dev.', ascending=False)
        if top_n is not None:
            df_skus = df_skus.head(top_n)
    
    return df_skus, total_devolucoes

def simular_reducao(vendas, matriz, full, max_date, dias_atras, reducao_percentual):
    """Simula o impacto de redução na taxa de devolução"""
    
    if matriz is None:
        matriz = pd.DataFrame()
    if full is None:
        full = pd.DataFrame()
    
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
    
    vendas_totais = len(vendas_periodo)
    faturamento_total = 0.0
    if 'Receita por produtos (BRL)' in vendas_periodo.columns:
        faturamento_total = float(vendas_periodo['Receita por produtos (BRL)'].fillna(0).sum())
    
    # Cenário atual
    devolucoes_atuais = 0
    impacto_atual = 0.0
    
    vendas_devolvidas = set()
    for _, venda in vendas_periodo.iterrows():
        num_venda = str(venda.get('N.º de venda', ''))
        if num_venda in dev_map and num_venda not in vendas_devolvidas:
            vendas_devolvidas.add(num_venda)
            devolucoes_atuais += 1
            for dev in dev_map[num_venda]:
                reembolso = dev.get('Cancelamentos e reembolsos (BRL)', None)
                if reembolso is None or pd.isna(reembolso):
                    reembolso = 0.0
                reembolso = float(reembolso)
                if reembolso == 0:
                    fallback = dev.get('Receita por produtos (BRL)', 0)
                    if pd.isna(fallback): fallback = 0.0
                    reembolso = float(fallback)
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
            'impacto': round(-impacto_atual, 2),
        },
        'cenario_simulado': {
            'devolucoes': devolucoes_simuladas,
            'taxa': round(taxa_simulada, 1),
            'impacto': round(-impacto_simulado, 2),
        },
        'economia': round(economia, 2),
        'reducao_percentual': reducao_percentual,
    }
