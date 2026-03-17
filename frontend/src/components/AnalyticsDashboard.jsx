import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Maximize2, Pencil, Trash2, X, TrendingUp, Hash, FileText } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';

const COLORS = ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#6366f1', '#14b8a6'];

const KPICards = ({ data }) => (
  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
    {data.map((kpi, i) => (
      <Card key={i} className="bg-gray-800/60 border-gray-700/50">
        <CardContent className="p-4 text-center">
          <p className="text-gray-400 text-xs mb-1 truncate">{kpi.label}</p>
          <p className={`font-bold ${kpi.format === 'text' ? 'text-lg text-emerald-400' : 'text-2xl text-white'}`}>
            {kpi.format === 'number' ? Number(kpi.value).toLocaleString() : kpi.value}
          </p>
        </CardContent>
      </Card>
    ))}
  </div>
);

const BarChartWidget = ({ chart }) => (
  <ResponsiveContainer width="100%" height={280}>
    <BarChart data={chart.data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
      <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 11 }} angle={-30} textAnchor="end" height={60} />
      <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} />
      <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#fff' }} />
      <Bar dataKey="value" fill={chart.color || '#8b5cf6'} radius={[4, 4, 0, 0]} />
    </BarChart>
  </ResponsiveContainer>
);

const LineChartWidget = ({ chart }) => (
  <ResponsiveContainer width="100%" height={280}>
    <LineChart data={chart.data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
      <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 11 }} angle={-30} textAnchor="end" height={60} />
      <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} />
      <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#fff' }} />
      <Line type="monotone" dataKey="value" stroke={chart.color || '#06b6d4'} strokeWidth={2} dot={{ fill: chart.color || '#06b6d4', r: 3 }} activeDot={{ r: 5 }} />
    </LineChart>
  </ResponsiveContainer>
);

const DonutChartWidget = ({ chart }) => (
  <ResponsiveContainer width="100%" height={280}>
    <PieChart>
      <Pie data={chart.data} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={3} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`} labelLine={{ stroke: '#6b7280' }}>
        {chart.data.map((_, i) => <Cell key={i} fill={(chart.colors || COLORS)[i % (chart.colors || COLORS).length]} />)}
      </Pie>
      <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#fff' }} />
      <Legend wrapperStyle={{ color: '#9ca3af', fontSize: 12 }} />
    </PieChart>
  </ResponsiveContainer>
);

const TableWidget = ({ chart }) => (
  <div className="overflow-x-auto max-h-[300px] overflow-y-auto">
    <table className="w-full text-sm">
      <thead className="sticky top-0 bg-gray-800">
        <tr>{(chart.columns || Object.keys(chart.data[0] || {})).map((col, i) => <th key={i} className="text-left py-2 px-3 text-gray-400 font-medium border-b border-gray-700">{col}</th>)}</tr>
      </thead>
      <tbody>
        {chart.data.map((row, i) => (
          <tr key={i} className="border-b border-gray-800 hover:bg-gray-800/50">
            {(chart.columns || Object.keys(row)).map((col, ci) => <td key={ci} className="py-2 px-3 text-gray-300">{row[col] !== null && row[col] !== undefined ? String(row[col]) : '-'}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

const ChartWidget = ({ chart, onDelete, onExpand }) => {
  if (chart.type === 'kpi') return <KPICards data={chart.data} />;

  return (
    <Card className="bg-gray-900 border-gray-800 group">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-white text-sm font-medium flex items-center">
            {chart.type === 'bar' && <Hash className="w-4 h-4 mr-2 text-purple-400" />}
            {chart.type === 'line' && <TrendingUp className="w-4 h-4 mr-2 text-cyan-400" />}
            {chart.type === 'donut' && <FileText className="w-4 h-4 mr-2 text-emerald-400" />}
            {chart.type === 'table' && <FileText className="w-4 h-4 mr-2 text-amber-400" />}
            {chart.title}
          </CardTitle>
          <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button onClick={() => onExpand(chart)} className="p-1 text-gray-500 hover:text-white"><Maximize2 className="w-3.5 h-3.5" /></button>
            <button onClick={() => onDelete(chart)} className="p-1 text-gray-500 hover:text-red-400"><Trash2 className="w-3.5 h-3.5" /></button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        {chart.type === 'bar' && <BarChartWidget chart={chart} />}
        {chart.type === 'line' && <LineChartWidget chart={chart} />}
        {chart.type === 'donut' && <DonutChartWidget chart={chart} />}
        {chart.type === 'table' && <TableWidget chart={chart} />}
      </CardContent>
    </Card>
  );
};

const AnalyticsDashboard = ({ charts, filename, onDeleteChart }) => {
  const [expandedChart, setExpandedChart] = useState(null);

  if (!charts || charts.length === 0) return null;

  const kpiChart = charts.find(c => c.type === 'kpi');
  const visualCharts = charts.filter(c => c.type !== 'kpi');

  return (
    <div className="space-y-4">
      {/* KPIs */}
      {kpiChart && <KPICards data={kpiChart.data} />}

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {visualCharts.map((chart, i) => (
          <ChartWidget key={i} chart={chart} onDelete={onDeleteChart || (() => {})} onExpand={setExpandedChart} />
        ))}
      </div>

      {/* Expanded Chart Modal */}
      <Dialog open={!!expandedChart} onOpenChange={() => setExpandedChart(null)}>
        <DialogContent className="bg-gray-900 border-gray-800 text-white max-w-5xl">
          <DialogHeader>
            <DialogTitle>{expandedChart?.title}</DialogTitle>
          </DialogHeader>
          <div className="py-4" style={{ height: 450 }}>
            {expandedChart?.type === 'bar' && <BarChartWidget chart={expandedChart} />}
            {expandedChart?.type === 'line' && <LineChartWidget chart={expandedChart} />}
            {expandedChart?.type === 'donut' && <DonutChartWidget chart={expandedChart} />}
            {expandedChart?.type === 'table' && <TableWidget chart={expandedChart} />}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AnalyticsDashboard;
