import { Card } from '@/components/ui/card';
import { ProcessedData } from '@/types/data';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface MatrizFullTabProps {
  data: ProcessedData;
}

export default function MatrizFullTab({ data }: MatrizFullTabProps) {
  const devoluções_matriz = data.devolucoesMatriz.length;
  const devoluções_full = data.devolucoesFull.length;

  const taxa_matriz = devoluções_matriz > 0 ? (devoluções_matriz / (devoluções_matriz + devoluções_full)) : 0;
  const taxa_full = devoluções_full > 0 ? (devoluções_full / (devoluções_matriz + devoluções_full)) : 0;

  const chartData = [
    { canal: 'Matriz', devoluções: devoluções_matriz, taxa: parseFloat((taxa_matriz * 100).toFixed(2)) },
    { canal: 'Full', devoluções: devoluções_full, taxa: parseFloat((taxa_full * 100).toFixed(2)) },
  ];

  const pieData = [
    { name: 'Matriz', value: devoluções_matriz },
    { name: 'Full', value: devoluções_full },
  ];

  const COLORS = ['#3b82f6', '#ef4444'];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="p-4 bg-blue-50 border-blue-200">
          <p className="text-sm text-gray-600">Devoluções Matriz</p>
          <p className="text-3xl font-bold text-blue-900">{devoluções_matriz}</p>
        </Card>
        <Card className="p-4 bg-red-50 border-red-200">
          <p className="text-sm text-gray-600">Devoluções Full</p>
          <p className="text-3xl font-bold text-red-900">{devoluções_full}</p>
        </Card>
        <Card className="p-4 bg-purple-50 border-purple-200">
          <p className="text-sm text-gray-600">Total</p>
          <p className="text-3xl font-bold text-purple-900">{devoluções_matriz + devoluções_full}</p>
        </Card>
      </div>

      <Card className="p-6">
        <h3 className="text-lg font-bold mb-4">Comparação</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="canal" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="devoluções" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </Card>

      <Card className="p-6">
        <h3 className="text-lg font-bold mb-4">Distribuição</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie data={pieData} cx="50%" cy="50%" outerRadius={80} fill="#8884d8" dataKey="value" label>
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </Card>
    </div>
  );
}
