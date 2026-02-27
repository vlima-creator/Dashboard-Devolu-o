// Tipos para dados de Vendas
export interface VendaRow {
  "N.º de venda": string;
  "Data da venda": Date;
  SKU: string;
  "Receita por produtos (BRL)": number;
  "Receita por envio (BRL)": number;
  "Custo de envio com base nas medidas e peso declarados": number;
  "Tarifas de venda e impostos (BRL)" | "Tarifa de venda e impostos (BRL)": number;
  "Venda por publicidade": string;
  [key: string]: any;
}

// Tipos para dados de Devoluções
export interface DevolucaoRow {
  "N.º de venda": string;
  "Cancelamentos e reembolsos (BRL)": number;
  "Tarifas de venda e impostos (BRL)" | "Tarifa de venda e impostos (BRL)": number;
  "Custo de envio com base nas medidas e peso declarados": number;
  Estado: string;
  "Motivo do resultado": string;
  "Forma de entrega": string;
  Canal: string;
  [key: string]: any;
}

// Tipos para dados processados
export interface ProcessedData {
  vendas: VendaRow[];
  devolucoesMatriz: DevolucaoRow[];
  devolucoesFull: DevolucaoRow[];
  maxDate: Date;
  totalLinhasVendas: number;
  totalLinhasDevolucoesMatriz: number;
  totalLinhasDevolucoesFull: number;
}

// Tipos para métricas
export interface Metricas {
  vendas: number;
  unidades: number;
  faturamento_produtos: number;
  faturamento_total: number;
  devolucoes_vendas: number;
  taxa_devolucao: number;
  faturamento_devolucoes: number;
  impacto_devolucao: number;
  perda_total: number;
  perda_parcial: number;
  saudaveis: number;
  criticas: number;
  neutras: number;
  impacto_saudaveis: number;
  impacto_criticas: number;
}

export interface MetricasPorJanela {
  janela: number;
  metricas: Metricas;
}

export interface MetricasPorSKU {
  sku: string;
  vendas: number;
  devolucoes: number;
  taxa_devolucao: number;
  impacto_devolucao: number;
  reembolsos: number;
  tarifas_devolucao: number;
  custo_devolucao: number;
  custo_envio: number;
  classe: "Saudável" | "Crítica" | "Neutra";
  score_risco: number;
}

export interface QualidadeArquivo {
  vendas: {
    sem_sku_pct: number;
    sem_data_pct: number;
    sem_numero_venda_pct: number;
  };
  devolucoesMatriz: {
    sem_motivo_pct: number;
    sem_estado_pct: number;
  };
  devolucoesFull: {
    sem_motivo_pct: number;
    sem_estado_pct: number;
  };
  custo_logistico_ausente: boolean;
}
