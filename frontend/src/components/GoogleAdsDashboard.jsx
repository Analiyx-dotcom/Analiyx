import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Loader2, RefreshCw, Eye, MousePointerClick, DollarSign, TrendingUp, Target, BarChart3 } from 'lucide-react';
import { toast } from '../hooks/use-toast';
import api from '../services/api';

const STATUS_COLORS = {
  ENABLED: 'bg-green-900/30 text-green-400 border-green-700',
  PAUSED: 'bg-yellow-900/30 text-yellow-400 border-yellow-700',
  REMOVED: 'bg-red-900/30 text-red-400 border-red-700',
  UNKNOWN: 'bg-gray-800 text-gray-400 border-gray-600',
};

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

const GoogleAdsDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [customers, setCustomers] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);

  const fetchCustomers = useCallback(async () => {
    try {
      const res = await api.get('/google-ads/customers');
      const list = res.data.customers || [];
      setCustomers(list);
      if (list.length > 0) {
        setSelectedCustomer(list[0]);
      }
    } catch { /* handled by fetchCampaigns */ }
  }, []);

  const fetchCampaigns = useCallback(async (customerId) => {
    setLoading(true);
    setError(null);
    try {
      const params = customerId ? `?customer_id=${customerId}` : '';
      const res = await api.get(`/google-ads/campaigns${params}`);
      setData(res.data);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to fetch Google Ads data.';
      setError(detail);
      if (!detail.includes('not connected')) {
        toast({ title: 'Google Ads Error', description: detail, variant: 'destructive' });
      }
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchCustomers(); }, [fetchCustomers]);

  useEffect(() => {
    if (selectedCustomer) {
      fetchCampaigns(selectedCustomer);
    } else {
      fetchCampaigns();
    }
  }, [selectedCustomer, fetchCampaigns]);

  if (loading) return <div className="flex items-center justify-center py-16"><Loader2 className="w-6 h-6 animate-spin text-purple-400" /><span className="ml-2 text-gray-400 text-sm">Loading Google Ads data...</span></div>;

  if (error) {
    return (
      <div className="text-center py-12" data-testid="google-ads-error">
        <BarChart3 className="w-10 h-10 text-gray-600 mx-auto mb-3" />
        <p className="text-gray-400 mb-1 text-sm">{error}</p>
        <Button size="sm" variant="outline" className="mt-3 border-purple-600 text-purple-400" onClick={() => fetchCampaigns(selectedCustomer)} data-testid="google-ads-retry">
          <RefreshCw className="w-3 h-3 mr-1" /> Retry
        </Button>
      </div>
    );
  }

  if (!data || !data.campaigns) return null;

  const { campaigns, summary } = data;
  const fmt = (n) => n?.toLocaleString('en-IN') ?? '0';
  const fmtCur = (n) => `₹${n?.toLocaleString('en-IN', { minimumFractionDigits: 2 }) ?? '0.00'}`;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2" data-testid="google-ads-title">
            <BarChart3 className="w-5 h-5 text-blue-400" /> Google Ads Performance
          </h3>
          <p className="text-gray-500 text-xs">Last 30 days &middot; Customer ID: {data.customer_id}</p>
        </div>
        <div className="flex items-center gap-2">
          {customers.length > 1 && (
            <select
              value={selectedCustomer || ''}
              onChange={(e) => setSelectedCustomer(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-2 py-1.5 text-xs text-gray-300 outline-none focus:border-purple-500"
              data-testid="google-ads-customer-select"
            >
              {customers.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          )}
          <Button size="sm" variant="ghost" onClick={() => fetchCampaigns(selectedCustomer)} className="text-gray-500 hover:text-white" data-testid="google-ads-refresh">
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3" data-testid="google-ads-summary">
        <SummaryCard icon={DollarSign} label="Total Spend" value={fmtCur(summary.total_cost)} sub={`${summary.total_campaigns} campaigns`} color="bg-purple-500/15 text-purple-400" />
        <SummaryCard icon={MousePointerClick} label="Total Clicks" value={fmt(summary.total_clicks)} sub={`CTR: ${summary.total_ctr}%`} color="bg-blue-500/15 text-blue-400" />
        <SummaryCard icon={Eye} label="Total Impressions" value={fmt(summary.total_impressions)} color="bg-cyan-500/15 text-cyan-400" />
        <SummaryCard icon={Target} label="Conversions" value={fmt(summary.total_conversions)} color="bg-green-500/15 text-green-400" />
      </div>

      {/* Campaigns Table */}
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-white text-sm flex items-center gap-2"><TrendingUp className="w-4 h-4 text-purple-400" /> Campaigns ({campaigns.length})</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {campaigns.length === 0 ? (
            <div className="text-center py-8 text-gray-500">No campaigns found in the last 30 days.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm" data-testid="google-ads-campaigns-table">
                <thead>
                  <tr className="border-b border-gray-800">
                    {['Campaign', 'Status', 'Type', 'Budget/day', 'Impressions', 'Clicks', 'CTR', 'Avg CPC', 'Cost', 'Conv.'].map(h => (
                      <th key={h} className="text-left py-3 px-3 text-gray-400 font-medium text-xs whitespace-nowrap">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {campaigns.map((c) => (
                    <tr key={c.id} className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">
                      <td className="py-2.5 px-3 text-white text-xs font-medium max-w-[200px] truncate" title={c.name}>{c.name}</td>
                      <td className="py-2.5 px-3"><Badge className={`${STATUS_COLORS[c.status] || STATUS_COLORS.UNKNOWN} text-[10px]`}>{c.status}</Badge></td>
                      <td className="py-2.5 px-3 text-gray-400 text-xs">{c.channel_type?.replace('_', ' ')}</td>
                      <td className="py-2.5 px-3 text-gray-300 text-xs">{fmtCur(c.daily_budget)}</td>
                      <td className="py-2.5 px-3 text-cyan-400 text-xs font-mono">{fmt(c.impressions)}</td>
                      <td className="py-2.5 px-3 text-blue-400 text-xs font-mono">{fmt(c.clicks)}</td>
                      <td className="py-2.5 px-3 text-yellow-400 text-xs font-mono">{c.ctr}%</td>
                      <td className="py-2.5 px-3 text-gray-300 text-xs font-mono">{fmtCur(c.avg_cpc)}</td>
                      <td className="py-2.5 px-3 text-purple-400 text-xs font-bold font-mono">{fmtCur(c.cost)}</td>
                      <td className="py-2.5 px-3 text-green-400 text-xs font-mono">{c.conversions}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default GoogleAdsDashboard;
