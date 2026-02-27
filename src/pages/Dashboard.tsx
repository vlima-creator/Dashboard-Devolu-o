import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Download } from 'lucide-react';
import { ProcessedData } from '@/types/data';
import { calcularMetricas, calcularQualidadeArquivo } from '@/lib/metricas';
import { exportarResultados } from '@/lib/export';
import ResumoTab from '@/components/tabs/ResumoTab';
import JanelasTab from '@/components/tabs/JanelasTab';
import MatrizFullTab from '@/components/tabs/MatrizFullTab';
import FreteTab from '@/components/tabs/FreteTab';
import MotivosTab from '@/components/tabs/MotivosTab';
import AdsTab from '@/components/tabs/AdsTab';
import SKUsTab from '@/components/tabs/SKUsTab';
import SimuladorTab from '@/components/tabs/SimuladorTab';

interface DashboardProps {
  data: ProcessedData;
  onReset: () => void;
}

export default function Dashboard({ data, onReset }: DashboardProps) {
  const [activeTab, setActiveTab] = useState('resumo');
  const [selectedJanela, setSelectedJanela] = useState(180);

  const metricas180 = calcularMetricas(data.vendas, data.devolucoesMatriz, data.devolucoesFull, data.maxDate, 180);
  const qualidade = calcularQualidadeArquivo(data);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              📊 Dashboard Vendas x Devoluções
            </h1>
            <p className="text-gray-600 mt-2">
              Referência: {data.maxDate.toLocaleDateString('pt-BR')} | 
              Janela padrão: 180 dias
            </p>
          </div>
          <div className="flex gap-2">
            <Button 
              onClick={() => exportarResultados(data)}
              className="bg-green-600 hover:bg-green-700 text-white"
            >
              <Download className="h-4 w-4 mr-2" />
              Exportar XLSX
            </Button>
            <Button onClick={onReset} variant="outline">
              ← Voltar
            </Button>
          </div>
        </div>

        {/* Info Banner */}
        <Card className="p-4 mb-8 bg-blue-50 border-blue-200">
          <p className="text-sm text-blue-900">
            <strong>Arquivos processados:</strong> {data.totalLinhasVendas} linhas de vendas | 
            {data.totalLinhasDevolucoesMatriz} devoluções Matriz | 
            {data.totalLinhasDevolucoesFull} devoluções Full
          </p>
        </Card>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-8 mb-8">
            <TabsTrigger value="resumo">Resumo</TabsTrigger>
            <TabsTrigger value="janelas">Janelas</TabsTrigger>
            <TabsTrigger value="matriz">Matriz/Full</TabsTrigger>
            <TabsTrigger value="frete">Frete</TabsTrigger>
            <TabsTrigger value="motivos">Motivos</TabsTrigger>
            <TabsTrigger value="ads">Ads</TabsTrigger>
            <TabsTrigger value="skus">SKUs</TabsTrigger>
            <TabsTrigger value="simulador">Simulador</TabsTrigger>
          </TabsList>

          <TabsContent value="resumo">
            <ResumoTab 
              data={data} 
              metricas={metricas180} 
              qualidade={qualidade}
            />
          </TabsContent>

          <TabsContent value="janelas">
            <JanelasTab 
              data={data}
              selectedJanela={selectedJanela}
              onJanelaChange={setSelectedJanela}
            />
          </TabsContent>

          <TabsContent value="matriz">
            <MatrizFullTab data={data} />
          </TabsContent>

          <TabsContent value="frete">
            <FreteTab data={data} />
          </TabsContent>

          <TabsContent value="motivos">
            <MotivosTab data={data} />
          </TabsContent>

          <TabsContent value="ads">
            <AdsTab data={data} />
          </TabsContent>

          <TabsContent value="skus">
            <SKUsTab data={data} selectedJanela={selectedJanela} />
          </TabsContent>

          <TabsContent value="simulador">
            <SimuladorTab 
              data={data}
              metricas={metricas180}
              selectedJanela={selectedJanela}
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
