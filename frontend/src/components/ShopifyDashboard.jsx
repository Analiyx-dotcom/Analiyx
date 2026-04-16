import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { ShoppingBag, RefreshCw, TrendingUp, DollarSign, Users, Package, ShoppingCart, Eye, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import api from '../services/api';

const COLORS = ['#96bf48', '#3b82f6', '#f59e0b', '#ec4899', '#10b981', '#8b5cf6'];

const ShopifyDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchReport = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/shopify/report');
      setData(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch Shopify data.');
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchReport(); }, [fetchReport]);

  if (loading) return <div className="flex items-center justify-center py-12"><div className="w-8 h-8 border-2 border-[#96bf48] border-t-transparent rounded-full animate-spin" /></div>;
  if (error) return (
    <div className="text-center py-12" data-testid="shopify-error">
      <ShoppingBag className="w-10 h-10 text-gray-600 mx-auto mb-3" />
      <p className="text-gray-400 mb-1 text-sm">{error}</p>
      <Button size="sm" variant="outline" className="mt-3 border-[#96bf48] text-[#96bf48]" onClick={fetchReport}><RefreshCw className="w-3 h-3 mr-1" /> Retry</Button>
    </div>
  );
  if (!data) return null;

  const { summary, daily_performance, top_products, recent_orders, traffic_sources } = data;
  const fmt = (n) => n?.toLocaleString('en-IN') ?? '0';
  const fmtCur = (n) => `₹${(n || 0).toLocaleString('en-IN')}`;

  const statusColor = {
    fulfilled: 'bg-green-900/30 text-green-400 border-green-800',
    processing: 'bg-blue-900/30 text-blue-400 border-blue-800',
    shipped: 'bg-amber-900/30 text-amber-400 border-amber-800',
    refunded: 'bg-red-900/30 text-red-400 border-red-800',
  };

  const productStatusColor = {
    active: 'bg-green-900/30 text-green-400 border-green-800',
    out_of_stock: 'bg-red-900/30 text-red-400 border-red-800',
    low_stock: 'bg-amber-900/30 text-amber-400 border-amber-800',
  };

  return (
    <div className="space-y-6" data-testid="shopify-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <ShoppingBag className="w-5 h-5 text-[#96bf48]" /> Shopify Store Analytics
          </h3>
          <p className="text-gray-500 text-xs">
            {data.store_name} — Last 30 days
            {data.is_sample_data && <Badge variant="outline" className="ml-2 text-yellow-500 border-yellow-600 text-[10px]">Sample Data</Badge>}
          </p>
        </div>
        <Button size="sm" variant="ghost" onClick={fetchReport} className="text-gray-500 hover:text-white"><RefreshCw className="w-4 h-4" /></Button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: 'Total Revenue', value: fmtCur(summary.total_revenue), icon: DollarSign, color: 'text-[#96bf48]' },
          { label: 'Orders', value: fmt(summary.total_orders), icon: ShoppingCart, color: 'text-blue-400' },
          { label: 'Visitors', value: fmt(summary.total_visitors), icon: Users, color: 'text-purple-400' },
          { label: 'Avg Order Value', value: fmtCur(summary.avg_order_value), icon: TrendingUp, color: 'text-cyan-400' },
          { label: 'Conversion Rate', value: `${summary.conversion_rate}%`, icon: ArrowUpRight, color: 'text-green-400' },
          { label: 'Returning Customers', value: `${summary.returning_customer_rate}%`, icon: Users, color: 'text-amber-400' },
          { label: 'Cart Abandonment', value: `${summary.cart_abandonment_rate}%`, icon: ArrowDownRight, color: 'text-red-400' },
          { label: 'Products Tracked', value: fmt(top_products.length), icon: Package, color: 'text-indigo-400' },
        ].map(({ label, value, icon: Icon, color }) => (
          <Card key={label} className="bg-gray-900 border-gray-800">
            <CardContent className="pt-4 pb-3 px-4">
              <div className="flex items-center justify-between mb-1">
                <span className="text-gray-500 text-xs">{label}</span>
                <Icon className={`w-4 h-4 ${color}`} />
              </div>
              <p className="text-white text-lg font-bold">{value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Revenue Trend */}
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Revenue & Orders Trend</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={daily_performance}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" tick={{ fill: '#9ca3af', fontSize: 10 }} interval={4} />
                <YAxis tick={{ fill: '#9ca3af', fontSize: 10 }} />
                <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#fff' }} />
                <Area type="monotone" dataKey="revenue" stroke="#96bf48" fill="#96bf48" fillOpacity={0.1} strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Traffic Sources */}
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Traffic Sources</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={traffic_sources} cx="50%" cy="50%" innerRadius={55} outerRadius={90} paddingAngle={3} dataKey="visitors" label={({ source, percent }) => `${source} ${(percent * 100).toFixed(0)}%`} labelLine={{ stroke: '#6b7280' }}>
                  {traffic_sources.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#fff' }} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Visitors & Conversion */}
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Visitors & Conversion Rate</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={daily_performance}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" tick={{ fill: '#9ca3af', fontSize: 10 }} interval={4} />
                <YAxis yAxisId="left" tick={{ fill: '#9ca3af', fontSize: 10 }} />
                <YAxis yAxisId="right" orientation="right" tick={{ fill: '#9ca3af', fontSize: 10 }} />
                <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#fff' }} />
                <Line yAxisId="left" type="monotone" dataKey="visitors" stroke="#3b82f6" strokeWidth={2} dot={false} />
                <Line yAxisId="right" type="monotone" dataKey="conversion_rate" stroke="#96bf48" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Orders per day */}
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Daily Orders</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={daily_performance}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" tick={{ fill: '#9ca3af', fontSize: 10 }} interval={4} />
                <YAxis tick={{ fill: '#9ca3af', fontSize: 10 }} />
                <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#fff' }} />
                <Bar dataKey="orders" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Top Products Table */}
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Top Products</CardTitle></CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm" data-testid="shopify-products-table">
              <thead><tr className="border-b border-gray-800">
                {['Product', 'SKU', 'Units Sold', 'Revenue', 'Inventory', 'Status'].map(h => <th key={h} className="text-left py-2 px-3 text-gray-500 font-medium text-xs">{h}</th>)}
              </tr></thead>
              <tbody>
                {top_products.map((p, i) => (
                  <tr key={i} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                    <td className="py-2.5 px-3 text-gray-200 font-medium">{p.name}</td>
                    <td className="py-2.5 px-3 text-gray-500 text-xs font-mono">{p.sku}</td>
                    <td className="py-2.5 px-3 text-gray-300">{fmt(p.sold)}</td>
                    <td className="py-2.5 px-3 text-[#96bf48]">{fmtCur(p.revenue)}</td>
                    <td className="py-2.5 px-3 text-gray-300">{fmt(p.inventory)}</td>
                    <td className="py-2.5 px-3"><Badge className={productStatusColor[p.status] || 'bg-gray-800 text-gray-400'}>{p.status.replace('_', ' ')}</Badge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Recent Orders Table */}
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Recent Orders</CardTitle></CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm" data-testid="shopify-orders-table">
              <thead><tr className="border-b border-gray-800">
                {['Order ID', 'Customer', 'Items', 'Total', 'Status', 'Date'].map(h => <th key={h} className="text-left py-2 px-3 text-gray-500 font-medium text-xs">{h}</th>)}
              </tr></thead>
              <tbody>
                {recent_orders.map((o, i) => (
                  <tr key={i} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                    <td className="py-2.5 px-3 text-gray-200 font-mono text-xs">{o.order_id}</td>
                    <td className="py-2.5 px-3 text-gray-300">{o.customer}</td>
                    <td className="py-2.5 px-3 text-gray-400">{o.items}</td>
                    <td className="py-2.5 px-3 text-white font-medium">{fmtCur(o.total)}</td>
                    <td className="py-2.5 px-3"><Badge className={statusColor[o.status] || 'bg-gray-800 text-gray-400'}>{o.status}</Badge></td>
                    <td className="py-2.5 px-3 text-gray-500 text-xs">{o.date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ShopifyDashboard;
