import * as XLSX from 'xlsx';
import { VendaRow, DevolucaoRow, ProcessedData } from '@/types/data';

// Meses em português
const MESES_PT: { [key: string]: number } = {
  janeiro: 1, fevereiro: 2, março: 3, abril: 4, maio: 5, junho: 6,
  julho: 7, agosto: 8, setembro: 9, outubro: 10, novembro: 11, dezembro: 12,
};

/**
 * Converte data no formato PT-BR "24 de fevereiro de 2026 22:51 hs." para Date
 */
export function parseDatePTBR(dateStr: string): Date | null {
  if (!dateStr || typeof dateStr !== 'string') return null;

  // Formato: "24 de fevereiro de 2026 22:51 hs."
  const regex = /(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})\s+(\d{2}):(\d{2})/i;
  const match = dateStr.match(regex);

  if (!match) return null;

  const [, dia, mesStr, ano, hora, minuto] = match;
  const mes = MESES_PT[mesStr.toLowerCase()];

  if (!mes) return null;

  return new Date(parseInt(ano), mes - 1, parseInt(dia), parseInt(hora), parseInt(minuto));
}

/**
 * Normaliza nomes de colunas (remove espaços extras, padroniza)
 */
export function normalizarColuna(col: string): string {
  return col.trim().toLowerCase();
}

/**
 * Encontra o índice da linha de cabeçalho procurando por colunas-chave
 */
export function encontrarCabecalho(
  sheet: XLSX.WorkSheet,
  colunasChave: string[]
): number {
  const range = XLSX.utils.decode_range(sheet['!ref'] || 'A1');
  
  for (let rowIdx = range.s.r; rowIdx <= Math.min(range.e.r, 50); rowIdx++) {
    const row: string[] = [];
    for (let colIdx = range.s.c; colIdx <= range.e.c; colIdx++) {
      const cellAddress = XLSX.utils.encode_cell({ r: rowIdx, c: colIdx });
      const cell = sheet[cellAddress];
      row.push(cell?.v?.toString().toLowerCase() || '');
    }

    // Verificar se todas as colunas-chave estão presentes
    const temTodasColunas = colunasChave.every(col =>
      row.some(cell => cell.includes(col.toLowerCase()))
    );

    if (temTodasColunas) {
      return rowIdx;
    }
  }

  return 0; // Assume primeira linha se não encontrar
}

/**
 * Normaliza dados de uma linha (converte números, datas, etc)
 */
export function normalizarLinha(
  row: any,
  colunas: string[],
  isDevolution: boolean = false
): any {
  const normalized: any = {};

  for (const col of colunas) {
    let value = row[col];

    // Converter datas
    if (col.toLowerCase().includes('data')) {
      if (typeof value === 'number') {
        // Excel serial date
        value = new Date((value - 25569) * 86400 * 1000);
      } else if (typeof value === 'string') {
        value = parseDatePTBR(value);
      }
    }

    // Converter números (BRL)
    if (col.toLowerCase().includes('brl') || col.toLowerCase().includes('receita') || 
        col.toLowerCase().includes('custo') || col.toLowerCase().includes('tarifa') ||
        col.toLowerCase().includes('reembolso')) {
      if (typeof value === 'string') {
        value = parseFloat(value.replace(/[^\d.-]/g, '')) || 0;
      } else if (typeof value === 'number') {
        value = value;
      } else {
        value = 0;
      }
    }

    normalized[col] = value;
  }

  return normalized;
}

/**
 * Lê arquivo Excel e extrai dados de Vendas
 */
export async function lerVendas(file: File): Promise<VendaRow[]> {
  const arrayBuffer = await file.arrayBuffer();
  const workbook = XLSX.read(arrayBuffer, { cellDates: true });
  const sheet = workbook.Sheets['Vendas BR'];

  if (!sheet) {
    throw new Error('Aba "Vendas BR" não encontrada');
  }

  const colunasChave = ['n.º de venda', 'data da venda', 'sku'];
  const cabecalhoIdx = encontrarCabecalho(sheet, colunasChave);

  // Ler dados começando do cabeçalho
  const dados = XLSX.utils.sheet_to_json(sheet, { header: 1 });
  const colunas = dados[cabecalhoIdx] as string[];
  const vendas: VendaRow[] = [];

  for (let i = cabecalhoIdx + 1; i < dados.length; i++) {
    const row = dados[i] as any[];
    if (!row || row.every(cell => !cell)) continue; // Pular linhas vazias

    const obj: any = {};
    colunas.forEach((col, idx) => {
      obj[col] = row[idx];
    });

    const normalizado = normalizarLinha(obj, colunas);
    vendas.push(normalizado as VendaRow);
  }

  return vendas;
}

/**
 * Lê arquivo Excel e extrai dados de Devoluções (Matriz e Full)
 */
export async function lerDevoluções(file: File): Promise<{
  matriz: DevolucaoRow[];
  full: DevolucaoRow[];
}> {
  const arrayBuffer = await file.arrayBuffer();
  const workbook = XLSX.read(arrayBuffer, { cellDates: true });

  const colunasChave = ['n.º de venda', 'estado', 'canal'];
  const resultado = { matriz: [] as DevolucaoRow[], full: [] as DevolucaoRow[] };

  // Processar aba "devoluções vendas matriz"
  const sheetMatriz = workbook.Sheets['devoluções vendas matriz'];
  if (sheetMatriz) {
    const cabecalhoIdx = encontrarCabecalho(sheetMatriz, colunasChave);
    const dados = XLSX.utils.sheet_to_json(sheetMatriz, { header: 1 });
    const colunas = dados[cabecalhoIdx] as string[];

    for (let i = cabecalhoIdx + 1; i < dados.length; i++) {
      const row = dados[i] as any[];
      if (!row || row.every(cell => !cell)) continue;

      const obj: any = {};
      colunas.forEach((col, idx) => {
        obj[col] = row[idx];
      });

      const normalizado = normalizarLinha(obj, colunas, true);
      resultado.matriz.push(normalizado as DevolucaoRow);
    }
  }

  // Processar aba "devoluções vendas full"
  const sheetFull = workbook.Sheets['devoluções vendas full'];
  if (sheetFull) {
    const cabecalhoIdx = encontrarCabecalho(sheetFull, colunasChave);
    const dados = XLSX.utils.sheet_to_json(sheetFull, { header: 1 });
    const colunas = dados[cabecalhoIdx] as string[];

    for (let i = cabecalhoIdx + 1; i < dados.length; i++) {
      const row = dados[i] as any[];
      if (!row || row.every(cell => !cell)) continue;

      const obj: any = {};
      colunas.forEach((col, idx) => {
        obj[col] = row[idx];
      });

      const normalizado = normalizarLinha(obj, colunas, true);
      resultado.full.push(normalizado as DevolucaoRow);
    }
  }

  return resultado;
}

/**
 * Processa arquivos e retorna dados consolidados
 */
export async function processarArquivos(
  vendaFile: File,
  devolucaoFile: File
): Promise<ProcessedData> {
  const vendas = await lerVendas(vendaFile);
  const { matriz, full } = await lerDevoluções(devolucaoFile);

  const maxDate = new Date(Math.max(
    ...vendas
      .map(v => v['Data da venda'] instanceof Date ? v['Data da venda'].getTime() : 0)
      .filter(d => d > 0)
  ));

  return {
    vendas,
    devolucoesMatriz: matriz,
    devolucoesFull: full,
    maxDate,
    totalLinhasVendas: vendas.length,
    totalLinhasDevolucoesMatriz: matriz.length,
    totalLinhasDevolucoesFull: full.length,
  };
}
