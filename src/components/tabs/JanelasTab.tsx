import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { ProcessedData, Metricas } from '@/types/data';
import { calcularMetricas } from '@/lib/metricas';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface JanelasTabProps {
  data: ProcessedData;
  selectedJanela: number;
  onJanelaChange: (janela: number) => void;
}

export default function JanelasTab({ data, selectedJanela, onJanelaChange }: JanelasTabProps) {
  const janelas = [30, 60, 90, 120, 150, 180];
  
  // Calcular métricas para todas as janelas
  const metricasPorJanela = janelas.map(janela => ({
    janela,
    metricas: calcularMetricas(data.vendas, data.devolucoesMatriz, data.devolucoesFull, data.maxDate, janela)
  }));

  // Dados para gráfico de linha
  const chartData = metricasPorJanela.map(item => ({
    janela: `${item.janela}d`,
    taxa: parseFloat((item.metricas.taxa_devolucao * 100).toFixed(2)),
    vendas: item.metricas.vendas,
    devolucoes: item.metricas.devolucoes_vendas,
  }));

  return (
    <div className="space-y-6">
      {/* Seletor de Janela */}
      <div className="flex gap-2 flex-wrap">
        {janelas.map(j => (
          <button
            key={j}
            onClick={() => onJanelaChange(j)}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              selectedJanela === j
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
            }`}
          >
            {j} dias
          </button>
        ))}
      </div>

      {/* Gráfico de Evolução */}
      <Card className="p-6">
        <h3 className="text-lg font-bold mb-4">Evolução da Taxa de Devolução</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="janela" />
            <YAxis yAxisId="left" label={{ value: 'Taxa (%)', angle: -90, position: 'insideLeft' }} />
            <YAxis yAxisId="right" orientation="right" label={{ value: 'Quantidade', angle: 90, position: 'insideRight' }} />
            <Tooltip />
            <Legend />
            <Line yAxisId="left" type="monotone" dataKey="taxa" stroke="#ef4444" name="Taxa de Devolução (%)" strokeWidth={2} />
            <Line yAxisId="right" type="monotone" dataKey="vendas" stroke="#3b82f6" name="Vendas" strokeWidth={2} />
            <Line yAxisId="right" type="monotone" dataKey="devolucoes" stroke="#f97316" name="Devoluções" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      {/* Tabela Consolidada */}
      <Card className="p-6 overflow-x-auto">
        <h3 className="text-lg font-bold mb-4">Consolidado por Período</h3>
        <table className="w-full text-sm">
          <thead className="bg-gray-100 border-b">
            <tr>
              <th className="px-4 py-2 text-left">Período</th>
              <th className="px-4 py-2 text-right">Vendas</th>
              <th className="px-4 py-2 text-right">Faturamento</th>
              <th className="px-4 py-2 text-right">Devoluções</th>
              <th className="px-4 py-2 text-right">Taxa</th>
              <th className="px-4 py-2 text-right">Faturamento Dev.</th>
              <th className="px-4 py-2 text-right">Perda Total</th>
              <th className="px-4 py-2 text-right">Perda Parcial</th>
              <th className="px-4 py-2 text-right">Saudáveis</th>
              <th className="px-4 py-2 text-right">Críticas</th>
            </tr>
          </thead>
          <tbody>
            {metricasPorJanela.map(item => (
              <tr key={item.janela} className="border-b hover:bg-gray-50">
                <td className="px-4 py-2 font-medium">{item.janela} dias</td>
                <td className="px-4 py-2 text-right">{item.metricas.vendas.toLocaleString('pt-BR')}</td>
                <td className="px-4 py-2 text-right">R$ {(item.metricas.faturamento_total / 1000).toFixed(1)}k</td>
                <td className="px-4 py-2 text-right">{item.metricas.devolucoes_vendas}</td>
                <td className="px-4 py-2 text-right font-bold text-red-600">
                  {(item.metricas.taxa_devolucao * 100).toFixed(2)}%
                </td>
                <td className="px-4 py-2 text-right">R$ {(item.metricas.faturamento_devolucoes / 1000).toFixed(1)}k</td>
                <td className="px-4 py-2 text-right text-red-600">R$ {(item.metricas.perda_total / 1000).toFixed(1)}k</td>
                <td className="px-4 py-2 text-right text-orange-600">R$ {(item.metricas.perda_parcial / 1000).toFixed(1)}k</td>
                <td className="px-4 py-2 text-right text-green-600">{item.metricas.saudaveis}</td>
                <td className="px-4 py-2 text-right text-red-600">{item.metricas.criticas}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      {/* Detalhes da Janela Selecionada */}
      <Card className="p-6">
        <h3 className="text-lg font-bold mb-4">Detalhes - {selectedJanela} dias</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {(() => {
            const m = metricasPorJanela.find(x => x.janela === selectedJanela)?.metricas;
            if (!m) return null;
            return (
              <>
                <div className="bg-blue-50 p-4 rounded">
                  <p className="text-sm text-gray-600">Impacto Saudáveis</p>
                  <p className="text-2xl font-bold text-green-600">R$ {(m.impacto_saudaveis / 1000).toFixed(1)}k</p>
                </div>
                <div className="bg-red-50 p-4 rounded">
                  <p className="text-sm text-gray-600">Impacto Críticas</p>
                  <p className="text-2xl font-bold text-red-600">R$ {(m.impacto_criticas / 1000).toFixed(1)}k</p>
                </div>
                <div className="bg-purple-50 p-4 rounded">
                  <p className="text-sm text-gray-600">Unidades</p>
                  <p className="text-2xl font-bold text-purple-600">{m.unidades}</p>
                </div>
                <div className="bg-orange-50 p-4 rounded">
                  <p className="text-sm text-gray-600">Devoluções Neutras</p>
                  <p className="text-2xl font-bold text-orange-600">{m.neutras}</p>
                </div>
              </>
            );
          })()}
        </div>
      </Card>
    </div>
  );
}
