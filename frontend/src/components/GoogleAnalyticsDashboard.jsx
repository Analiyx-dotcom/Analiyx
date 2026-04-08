import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Loader2, RefreshCw, Users, Eye, TrendingUp, Clock, UserPlus, BarChart3, Globe } from 'lucide-react';
import { toast } from '../hooks/use-toast';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';
import api from '../services/api';

const COLORS = ['#a855f7', '#3b82f6', '#22d3ee', '#22c55e', '#f59e0b', '#ef4444', '#ec4899', '#6366f1'];

const SummaryCard = ({ icon: Icon, label, value, sub, color }) => (
  <Card className="bg-gray-900 border-gray-800">
    <CardContent className="p-4 flex items-center gap-4">
      <div className={`w-11 h-11 rounded-xl flex items-center justify-center ${color}`}>
        <Icon className="w-5 h-5" />
      </div>
      <div>
        <p className="text-gray-400 text-xs">{label}</p>
        <p className="text-white text-xl font-bold leading-tight">{value}</p>
        {sub && <p className="text-gray-500 text-[10px]">{sub}</p>}
      </div>
    </CardContent>
  </Card>
);

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload) return null;
  return (
    <div className="bg-gray-900 border border-gray-700 rounded-lg p-3 shadow-xl text-xs">
      <p className="text-gray-400 mb-1">{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color }} className="font-medium">
          {p.name}: {typeof p.value === 'number' ? p.value.toLocaleString('en-IN') : p.value}
        </p>
      ))}
    </div>
  );
};

const GoogleAnalyticsDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [propertyId, setPropertyId] = useState('');
  const [needsPropertyId, setNeedsPropertyId] = useState(false);
  const [savingProp, setSavingProp] = useState(false);

  const fetchReport = useCallback(async (propId) => {
    setLoading(true);
    setError(null);
    try {
      const params = propId ? `?property_id=${propId}` : '';
      const res = await api.get(`/google-analytics/report${params}`);
      setData(res.data);
      setNeedsPropertyId(false);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to load analytics data.';
      if (detail.includes('not connected')) {
        setError(detail);
      } else if (detail.includes('No GA4 property')) {
        setNeedsPropertyId(true);
        setError(null);
      } else {
        setError(detail);
        toast({ title: 'Analytics Error', description: detail, variant: 'destructive' });
      }
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchReport(); }, [fetchReport]);

  const handleSetProperty = async () => {
    if (!propertyId.trim()) return;
    setSavingProp(true);
    try {
      await api.post('/google-analytics/set-property', { property_id: propertyId.trim() });
      toast({ title: 'Property Set', description: `GA4 Property ${propertyId} saved.` });
      fetchReport(propertyId.trim());
    } catch (err) {
      toast({ title: 'Error', description: err.response?.data?.detail || 'Failed to save.', variant: 'destructive' });
    } finally { setSavingProp(false); }
  };

  if (loading) return <div className="flex items-center justify-center py-16"><Loader2 className="w-6 h-6 animate-spin text-purple-400" /><span className="ml-2 text-gray-400 text-sm">Loading Google Analytics data...</span></div>;

  if (needsPropertyId) {
    return (
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader><CardTitle className="text-white text-sm flex items-center gap-2"><Globe className="w-5 h-5 text-orange-400" /> Google Analytics — Enter Property ID</CardTitle></CardHeader>
        <CardContent>
          <p className="text-gray-400 text-xs mb-3">We couldn't auto-detect your GA4 property. Enter your Property ID below.<br/>Find it in <span className="text-purple-400">Google Analytics &gt; Admin &gt; Property Settings</span> (looks like: 123456789)</p>
          <div className="flex gap-2">
            <input value={propertyId} onChange={(e) => setPropertyId(e.target.value)} placeholder="e.g. 123456789" className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm placeholder:text-gray-600" data-testid="ga-property-input" />
            <Button size="sm" onClick={handleSetProperty} disabled={!propertyId.trim() || savingProp} className="bg-gradient-to-r from-purple-600 to-pink-600" data-testid="ga-property-save">{savingProp ? <Loader2 className="w-3 h-3 animate-spin" /> : 'Load Data'}</Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <BarChart3 className="w-10 h-10 text-gray-600 mx-auto mb-3" />
        <p className="text-gray-400 mb-1">{error}</p>
        <Button size="sm" variant="outline" className="mt-3 border-purple-600 text-purple-400" onClick={fetchReport}>
          <RefreshCw className="w-3 h-3 mr-1" /> Retry
        </Button>
      </div>
    );
  }

  if (!data) return null;

  const { summary, daily_chart, top_pages, traffic_sources, period } = data;
  const fmt = (n) => n?.toLocaleString('en-IN') ?? '0';

  return (
    <div className="space-y-6" data-testid="ga-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Globe className="w-5 h-5 text-orange-400" /> Google Analytics
          </h3>
          <p className="text-gray-500 text-xs">{period} &middot; Property: {data.property_id}</p>
        </div>
        <Button size="sm" variant="ghost" onClick={() => fetchReport(data?.property_id)} className="text-gray-500 hover:text-white">
          <RefreshCw className="w-4 h-4" />
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
        <SummaryCard icon={Users} label="Total Users" value={fmt(summary.total_users)} color="bg-purple-500/15 text-purple-400" />
        <SummaryCard icon={TrendingUp} label="Sessions" value={fmt(summary.total_sessions)} color="bg-blue-500/15 text-blue-400" />
        <SummaryCard icon={Eye} label="Page Views" value={fmt(summary.total_pageviews)} color="bg-cyan-500/15 text-cyan-400" />
        <SummaryCard icon={UserPlus} label="New Users" value={fmt(summary.total_new_users)} color="bg-green-500/15 text-green-400" />
        <SummaryCard icon={Clock} label="Bounce Rate" value={`${summary.avg_bounce_rate}%`} color="bg-yellow-500/15 text-yellow-400" />
      </div>

      {/* Sessions & Users Line Chart */}
      {daily_chart.length > 0 && (
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Sessions & Users (Daily)</CardTitle></CardHeader>
          <CardContent>
            <div style={{ width: '100%', height: 300 }}>
              <ResponsiveContainer>
                <AreaChart data={daily_chart}>
                  <defs>
                    <linearGradient id="gaSessions" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#a855f7" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="gaUsers" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                  <XAxis dataKey="date" tick={{ fill: '#9ca3af', fontSize: 10 }} />
                  <YAxis tick={{ fill: '#9ca3af', fontSize: 10 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Area type="monotone" dataKey="sessions" stroke="#a855f7" fill="url(#gaSessions)" strokeWidth={2} name="Sessions" />
                  <Area type="monotone" dataKey="users" stroke="#3b82f6" fill="url(#gaUsers)" strokeWidth={2} name="Users" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Page Views & New Users Bar Chart */}
      {daily_chart.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Page Views (Daily)</CardTitle></CardHeader>
            <CardContent>
              <div style={{ width: '100%', height: 250 }}>
                <ResponsiveContainer>
                  <BarChart data={daily_chart}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                    <XAxis dataKey="date" tick={{ fill: '#9ca3af', fontSize: 10 }} />
                    <YAxis tick={{ fill: '#9ca3af', fontSize: 10 }} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="pageviews" fill="#22d3ee" radius={[3, 3, 0, 0]} name="Page Views" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Traffic Sources Pie Chart */}
          {traffic_sources.length > 0 && (
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Traffic Sources</CardTitle></CardHeader>
              <CardContent>
                <div style={{ width: '100%', height: 250 }}>
                  <ResponsiveContainer>
                    <PieChart>
                      <Pie data={traffic_sources} dataKey="sessions" nameKey="source" cx="50%" cy="50%" outerRadius={80} label={({ source, percent }) => `${source} ${(percent * 100).toFixed(0)}%`} labelLine={false}>
                        {traffic_sources.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                      </Pie>
                      <Tooltip content={<CustomTooltip />} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Top Pages Table */}
      {top_pages.length > 0 && (
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Top Pages</CardTitle></CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead><tr className="border-b border-gray-800">
                  {['Page Path', 'Page Views', 'Users', 'Bounce Rate'].map(h => <th key={h} className="text-left py-2.5 px-4 text-gray-400 font-medium text-xs">{h}</th>)}
                </tr></thead>
                <tbody>
                  {top_pages.map((p, i) => (
                    <tr key={i} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                      <td className="py-2 px-4 text-white text-xs font-mono max-w-[300px] truncate" title={p.page}>{p.page}</td>
                      <td className="py-2 px-4 text-cyan-400 text-xs font-mono">{fmt(p.pageviews)}</td>
                      <td className="py-2 px-4 text-purple-400 text-xs font-mono">{fmt(p.users)}</td>
                      <td className="py-2 px-4 text-yellow-400 text-xs font-mono">{p.bounce_rate}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default GoogleAnalyticsDashboard;
