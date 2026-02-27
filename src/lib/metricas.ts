import { VendaRow, DevolucaoRow, Metricas, ProcessedData, QualidadeArquivo } from '@/types/data';

/**
 * Classifica devolução como Saudável, Crítica ou Neutra
 */
export function classificarDevolucao(estado: string): 'Saudável' | 'Crítica' | 'Neutra' {
  if (!estado) return 'Neutra';

  const estadoLower = estado.toLowerCase();

  if (estadoLower.includes('te demos o dinheiro') || estadoLower.includes('liberamos o dinheiro')) {
    return 'Saudável';
  }

  if (
    estadoLower.includes('reembolso para o comprador') ||
    estadoLower.includes('cancelada pelo comprador') ||
    estadoLower.includes('mediação finalizada com reembolso')
  ) {
    return 'Crítica';
  }

  return 'Neutra';
}

/**
 * Calcula métricas para um período específico
 */
export function calcularMetricas(
  vendas: VendaRow[],
  devolucoesMatriz: DevolucaoRow[],
  devolucoesFull: DevolucaoRow[],
  maxDate: Date,
  diasAtras: number
): Metricas {
  const dataLimite = new Date(maxDate);
  dataLimite.setDate(dataLimite.getDate() - diasAtras);

  // Filtrar vendas no período
  const vendasPeriodo = vendas.filter(v => {
    const dataVenda = v['Data da venda'] instanceof Date ? v['Data da venda'] : new Date(v['Data da venda']);
    return dataVenda >= dataLimite && dataVenda <= maxDate;
  });

  // Criar mapa de devoluções por número de venda
  const todasDevoluções = [...devolucoesMatriz, ...devolucoesFull];
  const devolucoesPorVenda = new Map<string, DevolucaoRow[]>();

  todasDevoluções.forEach(dev => {
    const numeroVenda = dev['N.º de venda']?.toString();
    if (numeroVenda) {
      if (!devolucoesPorVenda.has(numeroVenda)) {
        devolucoesPorVenda.set(numeroVenda, []);
      }
      devolucoesPorVenda.get(numeroVenda)!.push(dev);
    }
  });

  // Calcular métricas
  const vendasTotais = vendasPeriodo.length;
  let unidades = 0;
  let faturamento_produtos = 0;
  let faturamento_total = 0;
  let devolucoes_vendas = 0;
  let faturamento_devolucoes = 0;
  let impacto_devolucao = 0;
  let perda_total = 0;
  let perda_parcial = 0;
  let saudaveis = 0;
  let criticas = 0;
  let neutras = 0;
  let impacto_saudaveis = 0;
  let impacto_criticas = 0;

  const vendaComDevolucao = new Set<string>();

  vendasPeriodo.forEach(venda => {
    const numeroVenda = venda['N.º de venda']?.toString();
    const receita_produtos = parseFloat(venda['Receita por produtos (BRL)']?.toString() || '0');
    const receita_envio = parseFloat(venda['Receita por envio (BRL)']?.toString() || '0');

    unidades += 1;
    faturamento_produtos += receita_produtos;
    faturamento_total += receita_produtos + receita_envio;

    // Verificar se tem devolução
    if (numeroVenda && devolucoesPorVenda.has(numeroVenda)) {
      vendaComDevolucao.add(numeroVenda);
      faturamento_devolucoes += receita_produtos;

      const devolucoesVenda = devolucoesPorVenda.get(numeroVenda)!;

      devolucoesVenda.forEach(dev => {
        const reembolsos = parseFloat(dev['Cancelamentos e reembolsos (BRL)']?.toString() || '0');
        const tarifas = parseFloat(dev['Tarifas de venda e impostos (BRL)']?.toString() || '0');
        const custo_logistico = parseFloat(dev['Custo de envio com base nas medidas e peso declarados']?.toString() || '0');

        const classe = classificarDevolucao(dev['Estado']);

        if (classe === 'Saudável') {
          saudaveis += 1;
          impacto_saudaveis += reembolsos + tarifas + custo_logistico;
        } else if (classe === 'Crítica') {
          criticas += 1;
          impacto_criticas += reembolsos + tarifas + custo_logistico;
        } else {
          neutras += 1;
        }

        // Impacto total
        impacto_devolucao += reembolsos + tarifas + custo_logistico;
        perda_total += reembolsos + tarifas + custo_logistico;
        perda_parcial += tarifas + custo_logistico;
      });
    }
  });

  devolucoes_vendas = vendaComDevolucao.size;
  const taxa_devolucao = vendasTotais > 0 ? devolucoes_vendas / vendasTotais : 0;

  return {
    vendas: vendasTotais,
    unidades,
    faturamento_produtos,
    faturamento_total,
    devolucoes_vendas,
    taxa_devolucao,
    faturamento_devolucoes,
    impacto_devolucao: -impacto_devolucao,
    perda_total: -perda_total,
    perda_parcial: -perda_parcial,
    saudaveis,
    criticas,
    neutras,
    impacto_saudaveis: -impacto_saudaveis,
    impacto_criticas: -impacto_criticas,
  };
}

/**
 * Calcula qualidade dos arquivos
 */
export function calcularQualidadeArquivo(data: ProcessedData): QualidadeArquivo {
  const { vendas, devolucoesMatriz, devolucoesFull } = data;

  // Qualidade Vendas
  const sem_sku = vendas.filter(v => !v.SKU).length;
  const sem_data = vendas.filter(v => !v['Data da venda']).length;
  const sem_numero = vendas.filter(v => !v['N.º de venda']).length;

  // Qualidade Devoluções Matriz
  const sem_motivo_matriz = devolucoesMatriz.filter(d => !d['Motivo do resultado']).length;
  const sem_estado_matriz = devolucoesMatriz.filter(d => !d['Estado']).length;

  // Qualidade Devoluções Full
  const sem_motivo_full = devolucoesFull.filter(d => !d['Motivo do resultado']).length;
  const sem_estado_full = devolucoesFull.filter(d => !d['Estado']).length;

  // Verificar se custo logístico está ausente
  const custo_ausente_matriz = devolucoesMatriz.every(d => !d['Custo de envio com base nas medidas e peso declarados']);
  const custo_ausente_full = devolucoesFull.every(d => !d['Custo de envio com base nas medidas e peso declarados']);

  return {
    vendas: {
      sem_sku_pct: (sem_sku / vendas.length) * 100,
      sem_data_pct: (sem_data / vendas.length) * 100,
      sem_numero_venda_pct: (sem_numero / vendas.length) * 100,
    },
    devolucoesMatriz: {
      sem_motivo_pct: (sem_motivo_matriz / devolucoesMatriz.length) * 100,
      sem_estado_pct: (sem_estado_matriz / devolucoesMatriz.length) * 100,
    },
    devolucoesFull: {
      sem_motivo_pct: (sem_motivo_full / devolucoesFull.length) * 100,
      sem_estado_pct: (sem_estado_full / devolucoesFull.length) * 100,
    },
    custo_logistico_ausente: custo_ausente_matriz || custo_ausente_full,
  };
}
