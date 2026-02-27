import { ProcessedData } from '@/types/data';
import { Card } from '@/components/ui/card';

interface JanelasTabProps {
  data: ProcessedData;
  selectedJanela: number;
  onJanelaChange: (janela: number) => void;
}

export default function JanelasTab({ data, selectedJanela, onJanelaChange }: JanelasTabProps) {
  return (
    <Card className="p-6">
      <h2 className="text-2xl font-bold mb-4">Análise por Janelas de Tempo</h2>
      <p className="text-gray-600">Componente em desenvolvimento...</p>
    </Card>
  );
}
