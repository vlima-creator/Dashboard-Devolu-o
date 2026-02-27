import { Card } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';
import { ProcessedData, Metricas, QualidadeArquivo } from '@/types/data';

interface ResumoTabProps {
  data: ProcessedData;
  metricas: Metricas;
  qualidade: QualidadeArquivo;
}

export default function ResumoTab({ data, metricas, qualidade }: ResumoTabProps) {
  return (
    <div className="space-y-6">
      {/* Qualidade do Arquivo */}
      <div>
        <h2 className="text-2xl font-bold mb-4">🔍 Qualidade do Arquivo</h2>
        
        {qualidade.custo_logistico_ausente && (
          <Alert className="mb-4 border-yellow-200 bg-yellow-50">
            <AlertCircle className="h-4 w-4 text-yellow-600" />
            <AlertDescription className="text-yellow-800">
              ⚠️ Custo de devolução não informado. Perdas totais/parciais podem estar subestimadas.
            </AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
          <Card className="p-4">
            <p className="text-sm text-gray-600">SKU sem informação</p>
            <p className="text-2xl font-bold text-red-600">{qualidade.vendas.sem_sku_pct.toFixed(1)}%</p>
          </Card>
          <Card className="p-4">
            <p className="text-sm text-gray-600">Data sem informação</p>
            <p className="text-2xl font-bold text-red-600">{qualidade.vendas.sem_data_pct.toFixed(1)}%</p>
          </Card>
          <Card className="p-4">
            <p className="text-sm text-gray-600">N.º de venda sem informação</p>
            <p className="text-2xl font-bold text-red-600">{qualidade.vendas.sem_numero_venda_pct.toFixed(1)}%</p>
          </Card>
          <Card className="p-4">
            <p className="text-sm text-gray-600">Devoluções Matriz - Sem motivo</p>
            <p className="text-2xl font-bold text-orange-600">{qualidade.devolucoesMatriz.sem_motivo_pct.toFixed(1)}%</p>
          </Card>
          <Card className="p-4">
            <p className="text-sm text-gray-600">Devoluções Matriz - Sem estado</p>
            <p className="text-2xl font-bold text-orange-600">{qualidade.devolucoesMatriz.sem_estado_pct.toFixed(1)}%</p>
          </Card>
          <Card className="p-4">
            <p className="text-sm text-gray-600">Devoluções Full - Sem motivo</p>
            <p className="text-2xl font-bold text-orange-600">{qualidade.devolucoesFull.sem_motivo_pct.toFixed(1)}%</p>
          </Card>
        </div>
      </div>

      {/* KPIs Principais */}
      <div>
        <h2 className="text-2xl font-bold mb-4">📊 KPIs Principais (180 dias)</h2>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <p className="text-sm text-gray-600 mb-2">Total de Vendas</p>
            <p className="text-3xl font-bold text-blue-900">{metricas.vendas.toLocaleString('pt-BR')}</p>
          </Card>

          <Card className="p-6 bg-gradient-to-br from-green-50 to-green-100 border-green-200">
            <p className="text-sm text-gray-600 mb-2">Faturamento Total</p>
            <p className="text-3xl font-bold text-green-900">
              R$ {(metricas.faturamento_total / 1000).toFixed(1)}k
            </p>
          </Card>

          <Card className="p-6 bg-gradient-to-br from-red-50 to-red-100 border-red-200">
            <p className="text-sm text-gray-600 mb-2">Taxa de Devolução</p>
            <p className="text-3xl font-bold text-red-900">{(metricas.taxa_devolucao * 100).toFixed(2)}%</p>
          </Card>

          <Card className="p-6 bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
            <p className="text-sm text-gray-600 mb-2">Impacto Financeiro</p>
            <p className="text-3xl font-bold text-orange-900">
              R$ {(metricas.impacto_devolucao / 1000).toFixed(1)}k
            </p>
          </Card>
        </div>
      </div>

      {/* Detalhes */}
      <div>
        <h2 className="text-2xl font-bold mb-4">📈 Detalhes</h2>
        
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <Card className="p-4">
            <p className="text-sm text-gray-600">Devoluções (vendas)</p>
            <p className="text-2xl font-bold">{metricas.devolucoes_vendas}</p>
          </Card>

          <Card className="p-4">
            <p className="text-sm text-gray-600">Faturamento Devoluções</p>
            <p className="text-2xl font-bold">R$ {(metricas.faturamento_devolucoes / 1000).toFixed(1)}k</p>
          </Card>

          <Card className="p-4">
            <p className="text-sm text-gray-600">Perda Total</p>
            <p className="text-2xl font-bold text-red-600">R$ {(metricas.perda_total / 1000).toFixed(1)}k</p>
          </Card>

          <Card className="p-4">
            <p className="text-sm text-gray-600">Devoluções Saudáveis</p>
            <p className="text-2xl font-bold text-green-600">{metricas.saudaveis}</p>
          </Card>

          <Card className="p-4">
            <p className="text-sm text-gray-600">Devoluções Críticas</p>
            <p className="text-2xl font-bold text-red-600">{metricas.criticas}</p>
          </Card>

          <Card className="p-4">
            <p className="text-sm text-gray-600">Devoluções Neutras</p>
            <p className="text-2xl font-bold text-gray-600">{metricas.neutras}</p>
          </Card>
        </div>
      </div>
    </div>
  );
}
