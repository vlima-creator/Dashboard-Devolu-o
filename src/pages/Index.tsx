import { useState } from 'react';
import { Upload, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { processarArquivos } from '@/lib/parser';
import { ProcessedData } from '@/types/data';
import Dashboard from './Dashboard';

export default function Index() {
  const [vendaFile, setVendaFile] = useState<File | null>(null);
  const [devolucaoFile, setDevolucaoFile] = useState<File | null>(null);
  const [processedData, setProcessedData] = useState<ProcessedData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, type: 'venda' | 'devolucao') => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.name.endsWith('.xlsx')) {
        setError('Por favor, selecione um arquivo .xlsx');
        return;
      }
      if (type === 'venda') {
        setVendaFile(file);
      } else {
        setDevolucaoFile(file);
      }
      setError(null);
    }
  };

  const handleProcessar = async () => {
    if (!vendaFile || !devolucaoFile) {
      setError('Por favor, selecione ambos os arquivos');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await processarArquivos(vendaFile, devolucaoFile);
      setProcessedData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao processar arquivos');
    } finally {
      setLoading(false);
    }
  };

  const handleCarregarExemplo = async () => {
    setLoading(true);
    setError(null);

    try {
      const vendaResponse = await fetch('/examples/vendas_exemplo.xlsx');
      const devolucaoResponse = await fetch('/examples/devolucoes_exemplo.xlsx');

      if (!vendaResponse.ok || !devolucaoResponse.ok) {
        throw new Error('Arquivos de exemplo não encontrados');
      }

      const vendaBlob = await vendaResponse.blob();
      const devolucaoBlob = await devolucaoResponse.blob();

      const vendaFile = new File([vendaBlob], 'vendas_exemplo.xlsx', { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const devolucaoFile = new File([devolucaoBlob], 'devolucoes_exemplo.xlsx', { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });

      setVendaFile(vendaFile);
      setDevolucaoFile(devolucaoFile);

      const data = await processarArquivos(vendaFile, devolucaoFile);
      setProcessedData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar exemplos');
    } finally {
      setLoading(false);
    }
  };

  if (processedData) {
    return <Dashboard data={processedData} onReset={() => setProcessedData(null)} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            📊 Dashboard Vendas x Devoluções
          </h1>
          <p className="text-lg text-gray-600">
            Análise automática de Vendas e Devoluções do Mercado Livre
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">{error}</AlertDescription>
          </Alert>
        )}

        {/* Upload Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Vendas Upload */}
          <Card className="p-6 border-2 border-dashed border-gray-300 hover:border-blue-500 transition">
            <div className="flex flex-col items-center justify-center h-48">
              <Upload className="h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Relatório de Vendas</h3>
              <p className="text-sm text-gray-600 text-center mb-4">
                Aba "Vendas BR"
              </p>
              <label className="cursor-pointer">
                <input
                  type="file"
                  accept=".xlsx"
                  onChange={(e) => handleFileChange(e, 'venda')}
                  className="hidden"
                />
                <span className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition inline-block">
                  Selecionar arquivo
                </span>
              </label>
              {vendaFile && (
                <p className="text-sm text-green-600 mt-4 font-medium">
                  ✓ {vendaFile.name}
                </p>
              )}
            </div>
          </Card>

          {/* Devoluções Upload */}
          <Card className="p-6 border-2 border-dashed border-gray-300 hover:border-blue-500 transition">
            <div className="flex flex-col items-center justify-center h-48">
              <Upload className="h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Relatório de Devoluções</h3>
              <p className="text-sm text-gray-600 text-center mb-4">
                Abas "devoluções vendas matriz" e "devoluções vendas full"
              </p>
              <label className="cursor-pointer">
                <input
                  type="file"
                  accept=".xlsx"
                  onChange={(e) => handleFileChange(e, 'devolucao')}
                  className="hidden"
                />
                <span className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition inline-block">
                  Selecionar arquivo
                </span>
              </label>
              {devolucaoFile && (
                <p className="text-sm text-green-600 mt-4 font-medium">
                  ✓ {devolucaoFile.name}
                </p>
              )}
            </div>
          </Card>
        </div>

        {/* Buttons */}
        <div className="flex gap-4 justify-center">
          <Button
            onClick={handleProcessar}
            disabled={!vendaFile || !devolucaoFile || loading}
            className="px-8 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400"
          >
            {loading ? 'Processando...' : 'Processar'}
          </Button>
          <Button
            onClick={handleCarregarExemplo}
            disabled={loading}
            variant="outline"
            className="px-8 py-2"
          >
            Carregar Exemplo
          </Button>
        </div>

        {/* Info */}
        <div className="mt-12 p-6 bg-white rounded-lg shadow-sm border border-gray-200">
          <h3 className="font-semibold text-gray-900 mb-3">ℹ️ Como usar:</h3>
          <ul className="space-y-2 text-sm text-gray-700">
            <li>1. Selecione o arquivo de Vendas (aba "Vendas BR")</li>
            <li>2. Selecione o arquivo de Devoluções (abas "devoluções vendas matriz" e "devoluções vendas full")</li>
            <li>3. Clique em "Processar" para gerar análise</li>
            <li>4. Ou clique em "Carregar Exemplo" para ver uma demonstração</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
