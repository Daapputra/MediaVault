import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const StatsChart = ({ original, compressed }) => {
  const data = [
    {
      name: 'Raw Pixels',
      size: original,
      color: '#475569' // slate-600
    },
    {
      name: 'Compressed',
      size: compressed,
      color: '#6c63ff' // primary
    }
  ];

  const formatYAxis = (tickItem) => {
    if (tickItem === 0) return '0';
    if (tickItem < 1024) return `${tickItem} B`;
    if (tickItem < 1024 * 1024) return `${(tickItem / 1024).toFixed(0)} KB`;
    return `${(tickItem / (1024 * 1024)).toFixed(1)} MB`;
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-surface border border-border p-3 rounded-lg shadow-xl">
          <p className="font-semibold text-text-primary mb-1">{label}</p>
          <p className="text-primary">
            {formatYAxis(payload[0].value)}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-48">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{ top: 20, right: 0, left: -20, bottom: 0 }}
          barSize={40}
        >
          <XAxis 
            dataKey="name" 
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#94a3b8', fontSize: 12 }}
            dy={10}
          />
          <YAxis 
            tickFormatter={formatYAxis}
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#94a3b8', fontSize: 12 }}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: '#252552', opacity: 0.4 }} />
          <Bar dataKey="size" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default StatsChart;
