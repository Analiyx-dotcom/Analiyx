import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { BookOpen, RefreshCw, DollarSign, TrendingUp, FileText, Users, Target, ArrowUpRight, Briefcase } from 'lucide-react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import api from '../services/api';

const COLORS = ['#e42527', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];

const ZohoDashboard = () => {
  const [booksData, setBooksData] = useState(null);
  const [crmData, setCrmData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeView, setActiveView] = useState('books');

  const fetchReports = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [booksRes, crmRes] = await Promise.all([
        api.get('/zoho/books/report'),
        api.get('/zoho/crm/report'),
      ]);
      setBooksData(booksRes.data);
      setCrmData(crmRes.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch Zoho data.');
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchReports(); }, [fetchReports]);

  if (loading) return <div className="flex items-center justify-center py-12"><div className="w-8 h-8 border-2 border-[#e42527] border-t-transparent rounded-full animate-spin" /></div>;
  if (error) return (
    <div className="text-center py-12" data-testid="zoho-error">
      <BookOpen className="w-10 h-10 text-gray-600 mx-auto mb-3" />
      <p className="text-gray-400 mb-1 text-sm">{error}</p>
      <Button size="sm" variant="outline" className="mt-3 border-[#e42527] text-[#e42527]" onClick={fetchReports}><RefreshCw className="w-3 h-3 mr-1" /> Retry</Button>
    </div>
  );

  const fmt = (n) => n?.toLocaleString('en-IN') ?? '0';
  const fmtCur = (n) => `₹${(n || 0).toLocaleString('en-IN')}`;

  const invoiceStatusColor = {
    paid: 'bg-green-900/30 text-green-400 border-green-800',
    overdue: 'bg-red-900/30 text-red-400 border-red-800',
    sent: 'bg-blue-900/30 text-blue-400 border-blue-800',
    draft: 'bg-gray-700/30 text-gray-400 border-gray-600',
  };

  const dealStageColor = {
    'Qualification': 'text-blue-400',
    'Needs Analysis': 'text-cyan-400',
    'Proposal': 'text-amber-400',
    'Negotiation': 'text-purple-400',
    'Closed Won': 'text-green-400',
    'Closed Lost': 'text-red-400',
  };

  const isSample = booksData?.is_sample_data || crmData?.is_sample_data;

  return (
    <div className="space-y-6" data-testid="zoho-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-[#e42527]" /> Zoho Analytics
          </h3>
          <p className="text-gray-500 text-xs">
            Books & CRM Overview
            {isSample && <Badge variant="outline" className="ml-2 text-yellow-500 border-yellow-600 text-[10px]">Sample Data</Badge>}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex bg-gray-800 rounded-lg p-0.5">
            <button onClick={() => setActiveView('books')} className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${activeView === 'books' ? 'bg-[#e42527] text-white' : 'text-gray-400 hover:text-white'}`} data-testid="zoho-books-tab">Books</button>
            <button onClick={() => setActiveView('crm')} className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${activeView === 'crm' ? 'bg-[#d0342c] text-white' : 'text-gray-400 hover:text-white'}`} data-testid="zoho-crm-tab">CRM</button>
          </div>
          <Button size="sm" variant="ghost" onClick={fetchReports} className="text-gray-500 hover:text-white"><RefreshCw className="w-4 h-4" /></Button>
        </div>
      </div>

      {/* ====== BOOKS VIEW ====== */}
      {activeView === 'books' && booksData && (
        <>
          {/* Books KPI Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { label: 'Total Income', value: fmtCur(booksData.summary.total_income), icon: DollarSign, color: 'text-green-400' },
              { label: 'Total Expenses', value: fmtCur(booksData.summary.total_expenses), icon: TrendingUp, color: 'text-red-400' },
              { label: 'Net Profit', value: fmtCur(booksData.summary.net_profit), icon: ArrowUpRight, color: 'text-[#96bf48]' },
              { label: 'Profit Margin', value: `${booksData.summary.profit_margin}%`, icon: Target, color: 'text-cyan-400' },
              { label: 'Total Invoiced', value: fmtCur(booksData.summary.total_invoiced), icon: FileText, color: 'text-blue-400' },
              { label: 'Paid', value: fmtCur(booksData.summary.paid_invoices), icon: DollarSign, color: 'text-emerald-400' },
              { label: 'Overdue', value: fmtCur(booksData.summary.overdue_amount), icon: FileText, color: 'text-red-400' },
              { label: 'Receivable', value: fmtCur(booksData.summary.accounts_receivable), icon: DollarSign, color: 'text-amber-400' },
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

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Income vs Expenses */}
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Income vs Expenses</CardTitle></CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={booksData.monthly_performance}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="month" tick={{ fill: '#9ca3af', fontSize: 10 }} />
                    <YAxis tick={{ fill: '#9ca3af', fontSize: 10 }} />
                    <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#fff' }} />
                    <Bar dataKey="income" fill="#10b981" radius={[4, 4, 0, 0]} name="Income" />
                    <Bar dataKey="expenses" fill="#ef4444" radius={[4, 4, 0, 0]} name="Expenses" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Expense Breakdown */}
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Expense Breakdown</CardTitle></CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie data={booksData.expense_categories} cx="50%" cy="50%" innerRadius={55} outerRadius={90} paddingAngle={3} dataKey="amount" label={({ category, percent }) => `${category.split(' ')[0]} ${(percent * 100).toFixed(0)}%`} labelLine={{ stroke: '#6b7280' }}>
                      {booksData.expense_categories.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#fff' }} />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Profit Trend */}
            <Card className="bg-gray-900 border-gray-800 lg:col-span-2">
              <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Monthly Profit Trend</CardTitle></CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={220}>
                  <AreaChart data={booksData.monthly_performance}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="month" tick={{ fill: '#9ca3af', fontSize: 11 }} />
                    <YAxis tick={{ fill: '#9ca3af', fontSize: 10 }} />
                    <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#fff' }} />
                    <Area type="monotone" dataKey="profit" stroke="#96bf48" fill="#96bf48" fillOpacity={0.15} strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Invoices Table */}
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Recent Invoices</CardTitle></CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm" data-testid="zoho-invoices-table">
                  <thead><tr className="border-b border-gray-800">
                    {['Invoice', 'Customer', 'Amount', 'Status', 'Issue Date', 'Due Date'].map(h => <th key={h} className="text-left py-2 px-3 text-gray-500 font-medium text-xs">{h}</th>)}
                  </tr></thead>
                  <tbody>
                    {booksData.invoices.map((inv, i) => (
                      <tr key={i} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                        <td className="py-2.5 px-3 text-gray-200 font-mono text-xs">{inv.invoice_id}</td>
                        <td className="py-2.5 px-3 text-gray-300">{inv.customer}</td>
                        <td className="py-2.5 px-3 text-white font-medium">{fmtCur(inv.amount)}</td>
                        <td className="py-2.5 px-3"><Badge className={invoiceStatusColor[inv.status] || 'bg-gray-800 text-gray-400'}>{inv.status}</Badge></td>
                        <td className="py-2.5 px-3 text-gray-500 text-xs">{inv.issue_date}</td>
                        <td className="py-2.5 px-3 text-gray-500 text-xs">{inv.due_date}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {/* ====== CRM VIEW ====== */}
      {activeView === 'crm' && crmData && (
        <>
          {/* CRM KPI Cards */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {[
              { label: 'Pipeline Value', value: fmtCur(crmData.summary.total_pipeline_value), icon: DollarSign, color: 'text-blue-400' },
              { label: 'Deals Won', value: fmtCur(crmData.summary.total_deals_won), icon: Target, color: 'text-green-400' },
              { label: 'Active Deals', value: fmt(crmData.summary.active_deals), icon: Briefcase, color: 'text-purple-400' },
              { label: 'Win Rate', value: `${crmData.summary.win_rate}%`, icon: ArrowUpRight, color: 'text-[#96bf48]' },
              { label: 'Avg Deal Size', value: fmtCur(crmData.summary.avg_deal_size), icon: DollarSign, color: 'text-amber-400' },
              { label: 'Total Leads', value: fmt(crmData.summary.total_leads), icon: Users, color: 'text-cyan-400' },
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

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Pipeline Funnel as Bar Chart */}
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Sales Pipeline</CardTitle></CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={crmData.pipeline_stages} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis type="number" tick={{ fill: '#9ca3af', fontSize: 10 }} />
                    <YAxis dataKey="stage" type="category" tick={{ fill: '#9ca3af', fontSize: 10 }} width={100} />
                    <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#fff' }} />
                    <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                      {crmData.pipeline_stages.map((entry, i) => (
                        <Cell key={i} fill={entry.stage === 'Closed Won' ? '#10b981' : entry.stage === 'Closed Lost' ? '#ef4444' : COLORS[i % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Lead Sources */}
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Lead Sources</CardTitle></CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie data={crmData.lead_sources} cx="50%" cy="50%" innerRadius={55} outerRadius={90} paddingAngle={3} dataKey="leads" label={({ source, percent }) => `${source} ${(percent * 100).toFixed(0)}%`} labelLine={{ stroke: '#6b7280' }}>
                      {crmData.lead_sources.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#fff' }} />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Monthly Deals Won */}
            <Card className="bg-gray-900 border-gray-800 lg:col-span-2">
              <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Monthly Deals (Won vs Lost)</CardTitle></CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={crmData.monthly_deals}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="month" tick={{ fill: '#9ca3af', fontSize: 11 }} />
                    <YAxis tick={{ fill: '#9ca3af', fontSize: 10 }} />
                    <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#fff' }} />
                    <Bar dataKey="won" fill="#10b981" radius={[4, 4, 0, 0]} name="Won" />
                    <Bar dataKey="lost" fill="#ef4444" radius={[4, 4, 0, 0]} name="Lost" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Recent Deals Table */}
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader className="pb-2"><CardTitle className="text-white text-sm">Recent Deals</CardTitle></CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm" data-testid="zoho-deals-table">
                  <thead><tr className="border-b border-gray-800">
                    {['Deal', 'Stage', 'Amount', 'Probability', 'Close Date', 'Owner'].map(h => <th key={h} className="text-left py-2 px-3 text-gray-500 font-medium text-xs">{h}</th>)}
                  </tr></thead>
                  <tbody>
                    {crmData.recent_deals.map((deal, i) => (
                      <tr key={i} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                        <td className="py-2.5 px-3 text-gray-200 font-medium">{deal.deal_name}</td>
                        <td className={`py-2.5 px-3 text-xs font-medium ${dealStageColor[deal.stage] || 'text-gray-400'}`}>{deal.stage}</td>
                        <td className="py-2.5 px-3 text-white font-medium">{fmtCur(deal.amount)}</td>
                        <td className="py-2.5 px-3 text-gray-300">{deal.probability}%</td>
                        <td className="py-2.5 px-3 text-gray-500 text-xs">{deal.close_date}</td>
                        <td className="py-2.5 px-3 text-gray-400">{deal.owner}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
};

export default ZohoDashboard;
