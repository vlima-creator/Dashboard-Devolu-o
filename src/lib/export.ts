import * as XLSX from 'xlsx';
import { ProcessedData, Metricas } from '@/types/data';
import { calcularMetricas, calcularQualidadeArquivo } from './metricas';

/**
 * Exporta os resultados do dashboard para um arquivo XLSX
 */
export function exportarResultados(data: ProcessedData, nomeArquivo: string = 'Dashboard_Vendas_Devolucoes.xlsx') {
  const workbook = XLSX.utils.book_new();

  // Aba 1: Resumo
  const resumoData = [];
  const metricas180 = calcularMetricas(data.vendas, data.devolucoesMatriz, data.devolucoesFull, data.maxDate, 180);
  const qualidade = calcularQualidadeArquivo(data);

  resumoData.push(['RESUMO EXECUTIVO - 180 DIAS']);
  resumoData.push([]);
  resumoData.push(['Métrica', 'Valor']);
  resumoData.push(['Total de Vendas', metricas180.vendas]);
  resumoData.push(['Faturamento Total (R$)', metricas180.faturamento_total]);
  resumoData.push(['Taxa de Devolução (%)', (metricas180.taxa_devolucao * 100).toFixed(2)]);
  resumoData.push(['Devoluções', metricas180.devolucoes_vendas]);
  resumoData.push(['Impacto Financeiro (R$)', metricas180.impacto_devolucao]);
  resumoData.push(['Perda Total (R$)', metricas180.perda_total]);
  resumoData.push(['Perda Parcial (R$)', metricas180.perda_parcial]);
  resumoData.push(['Devoluções Saudáveis', metricas180.saudaveis]);
  resumoData.push(['Devoluções Críticas', metricas180.criticas]);
  resumoData.push(['Devoluções Neutras', metricas180.neutras]);

  const wsResumo = XLSX.utils.aoa_to_sheet(resumoData);
  wsResumo['!cols'] = [{ wch: 30 }, { wch: 15 }];
  XLSX.utils.book_append_sheet(workbook, wsResumo, 'Resumo');

  // Aba 2: Qualidade do Arquivo
  const qualidadeData = [];
  qualidadeData.push(['QUALIDADE DO ARQUIVO']);
  qualidadeData.push([]);
  qualidadeData.push(['Métrica', 'Percentual']);
  qualidadeData.push(['SKU sem informação (%)', qualidade.vendas.sem_sku_pct.toFixed(2)]);
  qualidadeData.push(['Data sem informação (%)', qualidade.vendas.sem_data_pct.toFixed(2)]);
  qualidadeData.push(['N.º de venda sem informação (%)', qualidade.vendas.sem_numero_venda_pct.toFixed(2)]);
  qualidadeData.push(['Devoluções Matriz - Sem motivo (%)', qualidade.devolucoesMatriz.sem_motivo_pct.toFixed(2)]);
  qualidadeData.push(['Devoluções Matriz - Sem estado (%)', qualidade.devolucoesMatriz.sem_estado_pct.toFixed(2)]);
  qualidadeData.push(['Devoluções Full - Sem motivo (%)', qualidade.devolucoesFull.sem_motivo_pct.toFixed(2)]);
  qualidadeData.push(['Devoluções Full - Sem estado (%)', qualidade.devolucoesFull.sem_estado_pct.toFixed(2)]);
  qualidadeData.push(['Custo logístico ausente', qualidade.custo_logistico_ausente ? 'Sim' : 'Não']);

  const wsQualidade = XLSX.utils.aoa_to_sheet(qualidadeData);
  wsQualidade['!cols'] = [{ wch: 40 }, { wch: 15 }];
  XLSX.utils.book_append_sheet(workbook, wsQualidade, 'Qualidade');

  // Aba 3: Janelas de Tempo
  const janelasData = [];
  janelasData.push(['ANÁLISE POR JANELAS DE TEMPO']);
  janelasData.push([]);
  janelasData.push(['Período (dias)', 'Vendas', 'Faturamento (R$)', 'Devoluções', 'Taxa (%)', 'Perda Total (R$)']);

  const janelas = [30, 60, 90, 120, 150, 180];
  janelas.forEach(janela => {
    const m = calcularMetricas(data.vendas, data.devolucoesMatriz, data.devolucoesFull, data.maxDate, janela);
    janelasData.push([
      janela,
      m.vendas,
      m.faturamento_total.toFixed(2),
      m.devolucoes_vendas,
      (m.taxa_devolucao * 100).toFixed(2),
      m.perda_total.toFixed(2),
    ]);
  });

  const wsJanelas = XLSX.utils.aoa_to_sheet(janelasData);
  wsJanelas['!cols'] = [{ wch: 15 }, { wch: 12 }, { wch: 18 }, { wch: 12 }, { wch: 10 }, { wch: 18 }];
  XLSX.utils.book_append_sheet(workbook, wsJanelas, 'Janelas');

  // Aba 4: Matriz vs Full
  const matrizData = [];
  matrizData.push(['MATRIZ vs FULL']);
  matrizData.push([]);
  matrizData.push(['Canal', 'Devoluções', 'Percentual']);
  matrizData.push(['Matriz', data.devolucoesMatriz.length, ((data.devolucoesMatriz.length / (data.devolucoesMatriz.length + data.devolucoesFull.length)) * 100).toFixed(2)]);
  matrizData.push(['Full', data.devolucoesFull.length, ((data.devolucoesFull.length / (data.devolucoesMatriz.length + data.devolucoesFull.length)) * 100).toFixed(2)]);

  const wsMatriz = XLSX.utils.aoa_to_sheet(matrizData);
  wsMatriz['!cols'] = [{ wch: 15 }, { wch: 12 }, { wch: 12 }];
  XLSX.utils.book_append_sheet(workbook, wsMatriz, 'Matriz_Full');

  // Aba 5: Dados Brutos - Vendas
  const wsVendas = XLSX.utils.json_to_sheet(
    data.vendas.slice(0, 1000).map(v => ({
      'N.º de venda': v['N.º de venda'],
      'Data da venda': v['Data da venda'],
      'SKU': v.SKU,
      'Receita por produtos (BRL)': v['Receita por produtos (BRL)'],
      'Receita por envio (BRL)': v['Receita por envio (BRL)'],
    }))
  );
  wsVendas['!cols'] = [{ wch: 15 }, { wch: 20 }, { wch: 12 }, { wch: 18 }, { wch: 18 }];
  XLSX.utils.book_append_sheet(workbook, wsVendas, 'Vendas_Brutos');

  // Aba 6: Dados Brutos - Devoluções
  const devolucoesAll = [...data.devolucoesMatriz, ...data.devolucoesFull];
  const wsDevoluções = XLSX.utils.json_to_sheet(
    devolucoesAll.slice(0, 1000).map(d => ({
      'N.º de venda': d['N.º de venda'],
      'Cancelamentos e reembolsos (BRL)': d['Cancelamentos e reembolsos (BRL)'],
      'Estado': d['Estado'],
      'Motivo do resultado': d['Motivo do resultado'],
      'Canal': d['Canal'],
    }))
  );
  wsDevoluções['!cols'] = [{ wch: 15 }, { wch: 25 }, { wch: 20 }, { wch: 30 }, { wch: 12 }];
  XLSX.utils.book_append_sheet(workbook, wsDevoluções, 'Devolucoes_Brutos');

  // Salvar arquivo
  XLSX.writeFile(workbook, nomeArquivo);
}
