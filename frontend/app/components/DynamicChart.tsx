'use client';

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  PieChart, Pie, Cell,
  LineChart, Line
} from 'recharts';

interface ChartProps {
  chartType: string;
  data: any[];
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#AF19FF'];

const DynamicChart = ({ chartType, data }: ChartProps) => {
  if (!data || data.length === 0) {
    return <div className="flex items-center justify-center h-full text-gray-500">No data to display.</div>;
  }

  if (typeof data[0] !== 'object' || data[0] === null) {
    return <div className="text-red-500">Invalid data format.</div>;
  }

  const keys = Object.keys(data[0]);
  const nameKey = keys[0];
  const valueKey = keys[1];

  // --- Final Change: We remove ResponsiveContainer and set a fixed size ---

  const type = chartType.toLowerCase().trim();

  if (type.includes('bar')) {
    return (
      <BarChart width={700} height={400} data={data} margin={{ top: 5, right: 20, left: 10, bottom: 50 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={nameKey} angle={-35} textAnchor="end" interval={0} />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey={valueKey} fill="#8884d8" />
      </BarChart>
    );
  }

  if (type.includes('pie')) {
    return (
      <PieChart width={700} height={400}>
        <Pie data={data} dataKey={valueKey} nameKey={nameKey} cx="50%" cy="50%" outerRadius={150} fill="#8884d8" label>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    );
  }

  if (type.includes('line')) {
    return (
      <LineChart width={700} height={400} data={data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={nameKey} />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey={valueKey} stroke="#8884d8" activeDot={{ r: 8 }} />
      </LineChart>
    );
  }

  return <div className="text-red-500">Unsupported chart type: "{chartType}"</div>;
};

export default DynamicChart;