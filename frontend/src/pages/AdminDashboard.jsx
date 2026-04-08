import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { adminAPI } from '../services/api';
import { Users, DollarSign, Database, TrendingUp, ArrowUp, ArrowDown, LogOut, Sparkles, Menu, X, MessageSquare, CheckCircle, Loader2, Download, ShieldAlert, Clock, Send, FileText, Ban, Shield, Search, Tag, Plus, Trash2, ToggleLeft, ToggleRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { toast } from '../hooks/use-toast';
import api from '../services/api';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState({ total_users: 0, active_subscriptions: 0, monthly_revenue: 0, data_sources: 0 });
  const [detailedUsers, setDetailedUsers] = useState([]);
  const [userGrowthData, setUserGrowthData] = useState([]);
  const [revenueData, setRevenueData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [slackToken, setSlackToken] = useState('');
  const [slackConnected, setSlackConnected] = useState(false);
  const [slackTeam, setSlackTeam] = useState('');
  const [isConnectingSlack, setIsConnectingSlack] = useState(false);
  const [tickets, setTickets] = useState([]);
  const [replyText, setReplyText] = useState({});
  const [expandedTicket, setExpandedTicket] = useState(null);
  const [userSearchQuery, setUserSearchQuery] = useState('');
  const [coupons, setCoupons] = useState([]);
  const [newCouponCode, setNewCouponCode] = useState('');
  const [newCouponDiscount, setNewCouponDiscount] = useState('');

  useEffect(() => {
    const userData = localStorage.getItem('user');
    const token = localStorage.getItem('token');
    if (!userData || !token) { navigate('/login'); return; }
    try {
      const parsed = JSON.parse(userData);
      const isAdmin = parsed.role === 'admin' || parsed.email === 'Admin@analiyx.com' || parsed.email === 'admin@analiyx.com';
      if (!isAdmin) { navigate('/dashboard'); return; }
      fetchDashboardData();
    } catch { navigate('/login'); }
  }, [navigate]);

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      const [statsData, userGrowth, revenue, detailedUsersData] = await Promise.all([
        adminAPI.getStats(),
        adminAPI.getUserGrowth(),
        adminAPI.getRevenue(),
        adminAPI.getAllUsersDetails()
      ]);
      setStats(statsData);
      setUserGrowthData(userGrowth.data || []);
      setRevenueData(revenue.data || []);
      setDetailedUsers(detailedUsersData.users || []);
      try {
        const slackStatus = await api.get('/slack/status');
        if (slackStatus.data.connected) {
          setSlackConnected(true);
          setSlackTeam(slackStatus.data.team_name || '');
        }
      } catch {}
    } catch (error) {
      if (error.response?.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        navigate('/login');
      }
    } finally { setIsLoading(false); }
  };

  const fetchTickets = async () => {
    try {
      const data = await adminAPI.getAllTickets();
      setTickets(data.tickets || []);
    } catch {}
  };

  useEffect(() => {
    if (activeTab === 'tickets') fetchTickets();
    if (activeTab === 'coupons') fetchCoupons();
  }, [activeTab]);

  const fetchCoupons = async () => {
    try {
      const res = await api.get('/admin/manage/coupons');
      setCoupons(res.data.coupons || []);
    } catch {}
  };

  const handleCreateCoupon = async () => {
    if (!newCouponCode.trim() || !newCouponDiscount) return;
    const discount = parseInt(newCouponDiscount);
    if (isNaN(discount) || discount < 1 || discount > 100) {
      toast({ title: 'Error', description: 'Discount must be between 1 and 100', variant: 'destructive' });
      return;
    }
    try {
      await api.post('/admin/manage/coupons', { code: newCouponCode.trim(), discount_percentage: discount });
      setNewCouponCode('');
      setNewCouponDiscount('');
      fetchCoupons();
      toast({ title: 'Coupon Created', description: `Coupon ${newCouponCode.toUpperCase()} created.` });
    } catch (error) {
      toast({ title: 'Error', description: error.response?.data?.detail || 'Failed to create coupon.', variant: 'destructive' });
    }
  };

  const handleToggleCoupon = async (couponId) => {
    try {
      await api.put(`/admin/manage/coupons/${couponId}/toggle`);
      fetchCoupons();
    } catch {}
  };

  const handleDeleteCoupon = async (couponId) => {
    if (!window.confirm('Delete this coupon?')) return;
    try {
      await api.delete(`/admin/manage/coupons/${couponId}`);
      fetchCoupons();
      toast({ title: 'Deleted', description: 'Coupon deleted.' });
    } catch {}
  };

  const handleUpdateUserStatus = async (userId, newStatus) => {
    try {
      await adminAPI.updateUserStatus(userId, newStatus);
      const data = await adminAPI.getAllUsersDetails();
      setDetailedUsers(data.users || []);
      const msgs = { active: 'activated', disabled: 'disabled', spam: 'blocked as spam' };
      toast({ title: 'Success', description: `User ${msgs[newStatus] || newStatus}.` });
    } catch (error) {
      toast({ title: 'Error', description: error.response?.data?.detail || 'Failed to update user.', variant: 'destructive' });
    }
  };

  const handleExtendTrial = async (userId) => {
    try {
      const result = await adminAPI.extendTrial(userId, 7);
      const data = await adminAPI.getAllUsersDetails();
      setDetailedUsers(data.users || []);
      toast({ title: 'Trial Extended', description: result.message || 'Extended by 7 days.' });
    } catch (error) {
      toast({ title: 'Error', description: error.response?.data?.detail || 'Failed.', variant: 'destructive' });
    }
  };

  const handleExtendSubscription = async (userId, months) => {
    try {
      const result = await adminAPI.updateSubscription(userId, months);
      const data = await adminAPI.getAllUsersDetails();
      setDetailedUsers(data.users || []);
      toast({ title: 'Subscription Extended', description: result.message });
    } catch (error) {
      toast({ title: 'Error', description: error.response?.data?.detail || 'Failed.', variant: 'destructive' });
    }
  };

  const handleManageCredits = async (userId, action) => {
    const credits = prompt(`Enter number of credits to ${action}:`, '100');
    if (!credits || isNaN(credits)) return;
    try {
      await adminAPI.manageCredits(userId, parseInt(credits), action);
      const data = await adminAPI.getAllUsersDetails();
      setDetailedUsers(data.users || []);
      toast({ title: 'Credits Updated', description: `Credits ${action}ed successfully.` });
    } catch (error) {
      toast({ title: 'Error', description: error.response?.data?.detail || 'Failed.', variant: 'destructive' });
    }
  };

  const handleReplyTicket = async (ticketId) => {
    const text = replyText[ticketId];
    if (!text?.trim()) return;
    try {
      await adminAPI.replyToTicket(ticketId, text);
      setReplyText(prev => ({ ...prev, [ticketId]: '' }));
      fetchTickets();
      toast({ title: 'Reply Sent' });
    } catch (error) {
      toast({ title: 'Error', description: 'Failed to send reply.', variant: 'destructive' });
    }
  };

  const handleCloseTicket = async (ticketId) => {
    try {
      await adminAPI.closeTicket(ticketId);
      fetchTickets();
      toast({ title: 'Ticket Closed' });
    } catch {}
  };

  const handleExportUsers = async (format) => {
    try {
      const token = localStorage.getItem('token');
      const url = format === 'excel' ? adminAPI.exportUsersExcel() : adminAPI.exportUsersPDF();
      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Export failed');
      const blob = await response.blob();
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = format === 'excel' ? 'analiyx_users.xlsx' : 'analiyx_users.pdf';
      link.click();
      URL.revokeObjectURL(link.href);
      toast({ title: 'Export Complete', description: `Users exported as ${format.toUpperCase()}` });
    } catch {
      toast({ title: 'Export Failed', description: 'Could not export users.', variant: 'destructive' });
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const handleConnectSlack = async () => {
    if (!slackToken.trim()) return;
    setIsConnectingSlack(true);
    try {
      const res = await api.post('/slack/connect', { bot_token: slackToken });
      setSlackConnected(true);
      setSlackTeam(res.data.team_name || '');
      setSlackToken('');
      toast({ title: 'Slack Connected!', description: `Connected to ${res.data.team_name}` });
    } catch (error) {
      toast({ title: 'Connection Failed', description: error.response?.data?.detail || 'Invalid bot token', variant: 'destructive' });
    } finally { setIsConnectingSlack(false); }
  };

  const handleDisconnectSlack = async () => {
    try {
      await api.delete('/slack/disconnect');
      setSlackConnected(false);
      setSlackTeam('');
      toast({ title: 'Disconnected', description: 'Slack workspace disconnected.' });
    } catch { toast({ title: 'Error', description: 'Failed to disconnect.', variant: 'destructive' }); }
  };

  const sidebarItems = [
    { id: 'dashboard', label: 'Dashboard', icon: TrendingUp },
    { id: 'users', label: 'Users', icon: Users },
    { id: 'tickets', label: 'Tickets', icon: MessageSquare },
    { id: 'coupons', label: 'Coupons', icon: Tag },
    { id: 'datasources', label: 'Data Sources', icon: Database },
    { id: 'revenue', label: 'Revenue', icon: DollarSign },
    { id: 'slack', label: 'Slack', icon: MessageSquare },
  ];

  const formatINR = (amount) => `₹${Number(amount).toLocaleString('en-IN')}`;

  const statusColor = (status) => {
    if (status === 'active') return 'bg-green-900/30 text-green-400 border-green-700';
    if (status === 'spam') return 'bg-red-900/30 text-red-400 border-red-700';
    return 'bg-yellow-900/30 text-yellow-400 border-yellow-700';
  };

  const adminStatsDisplay = [
    { label: 'Total Users', value: stats.total_users.toLocaleString(), change: '+12.5%', trend: 'up', icon: Users },
    { label: 'Active Subscriptions', value: stats.active_subscriptions.toLocaleString(), change: '+8.2%', trend: 'up', icon: TrendingUp },
    { label: 'Monthly Revenue', value: formatINR(stats.monthly_revenue), change: '+15.3%', trend: 'up', icon: DollarSign },
    { label: 'Data Sources', value: stats.data_sources.toLocaleString(), change: '+22.1%', trend: 'up', icon: Database }
  ];

  const renderDashboardTab = () => (
    <div className="space-y-8">
      <div><h1 className="text-3xl font-bold text-white mb-2">Dashboard Overview</h1><p className="text-gray-400">Monitor your platform's key metrics and performance</p></div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {adminStatsDisplay.map((stat, index) => (
          <Card key={index} className="bg-gray-900 border-gray-800 hover:border-purple-500/50 transition-all">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-purple-900/20 rounded-lg"><stat.icon className="w-6 h-6 text-purple-400" /></div>
                <div className={`flex items-center text-sm font-semibold ${stat.trend === 'up' ? 'text-green-500' : 'text-red-500'}`}>
                  {stat.trend === 'up' ? <ArrowUp className="w-4 h-4 mr-1" /> : <ArrowDown className="w-4 h-4 mr-1" />}{stat.change}
                </div>
              </div>
              <p className="text-gray-400 text-sm mb-1">{stat.label}</p>
              <p className="text-3xl font-bold text-white">{stat.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader><CardTitle className="text-white">User Growth</CardTitle></CardHeader>
          <CardContent>
            {isLoading ? <div className="h-64 flex items-center justify-center text-gray-400">Loading...</div> : (
              <div className="h-64 flex items-end justify-between space-x-2 px-2">
                {userGrowthData.map((data, i) => {
                  const max = Math.max(...userGrowthData.map(d => d.users), 1);
                  const h = Math.max((data.users / max) * 100, 4);
                  return (<div key={i} className="flex-1 flex flex-col items-center h-full justify-end"><div className="w-full bg-gradient-to-t from-purple-600 to-pink-600 rounded-t-lg hover:from-purple-500 hover:to-pink-500 transition-all min-h-[4px]" style={{ height: `${h}%` }}></div><span className="text-xs text-gray-500 mt-2">{data.month}</span></div>);
                })}
              </div>
            )}
          </CardContent>
        </Card>
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader><CardTitle className="text-white">Revenue Trend (INR)</CardTitle></CardHeader>
          <CardContent>
            {isLoading ? <div className="h-64 flex items-center justify-center text-gray-400">Loading...</div> : (
              <div className="h-64 flex items-end justify-between space-x-2 px-2">
                {revenueData.map((data, i) => {
                  const max = Math.max(...revenueData.map(d => d.amount), 1);
                  const h = Math.max((data.amount / max) * 100, 4);
                  return (<div key={i} className="flex-1 flex flex-col items-center h-full justify-end"><div className="w-full bg-gradient-to-t from-green-600 to-emerald-600 rounded-t-lg hover:from-green-500 hover:to-emerald-500 transition-all min-h-[4px]" style={{ height: `${h}%` }}></div><span className="text-xs text-gray-500 mt-2">{data.month}</span></div>);
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );

  const renderUsersTab = () => {
    const filteredUsers = userSearchQuery.trim()
      ? detailedUsers.filter(u => 
          (u.client_id || '').toLowerCase().includes(userSearchQuery.toLowerCase()) ||
          (u.phone || '').toLowerCase().includes(userSearchQuery.toLowerCase()) ||
          (u.name || '').toLowerCase().includes(userSearchQuery.toLowerCase()) ||
          (u.email || '').toLowerCase().includes(userSearchQuery.toLowerCase())
        )
      : detailedUsers;

    return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div><h1 className="text-3xl font-bold text-white mb-2">User Management</h1><p className="text-gray-400">Manage all registered users</p></div>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm" onClick={() => handleExportUsers('excel')} className="border-green-500 text-green-400 hover:bg-green-900/20" data-testid="export-excel-btn"><Download className="w-4 h-4 mr-1" /> Excel</Button>
          <Button variant="outline" size="sm" onClick={() => handleExportUsers('pdf')} className="border-blue-500 text-blue-400 hover:bg-blue-900/20" data-testid="export-pdf-btn"><FileText className="w-4 h-4 mr-1" /> PDF</Button>
          <Button variant="outline" size="sm" onClick={fetchDashboardData} className="border-purple-500 text-purple-400">Refresh</Button>
        </div>
      </div>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500" />
        <Input
          value={userSearchQuery}
          onChange={(e) => setUserSearchQuery(e.target.value)}
          placeholder="Search by Client ID, Phone, Name or Email..."
          className="bg-gray-800 border-gray-700 text-white pl-10"
          data-testid="admin-user-search"
        />
      </div>
      <Card className="bg-gray-900 border-gray-800">
        <CardContent className="p-0">
          {isLoading ? <div className="text-center py-8 text-gray-400">Loading...</div> : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead><tr className="border-b border-gray-800">
                  {['Client ID', 'Name', 'Phone', 'Email', 'Plan', 'Credits', 'Status', 'Company', 'Industry', 'Sub. End', 'Joined', 'Actions'].map(h => <th key={h} className="text-left py-3 px-4 text-gray-400 font-medium">{h}</th>)}
                </tr></thead>
                <tbody>
                  {filteredUsers.map((u) => (
                    <tr key={u.id} className="border-b border-gray-800 hover:bg-gray-800/50">
                      <td className="py-3 px-4 text-purple-400 font-mono text-xs" data-testid={`user-client-id-${u.id}`}>{u.client_id || '-'}</td>
                      <td className="py-3 px-4 text-white">{u.name}</td>
                      <td className="py-3 px-4 text-gray-400 text-xs" data-testid={`user-phone-${u.id}`}>{u.phone || '-'}</td>
                      <td className="py-3 px-4 text-gray-400 text-xs">{u.email}</td>
                      <td className="py-3 px-4"><Badge variant="secondary" className="bg-purple-900/30 text-purple-400 border-purple-700">{u.plan}</Badge></td>
                      <td className="py-3 px-4 text-white">{u.credits}</td>
                      <td className="py-3 px-4"><Badge className={statusColor(u.status)}>{u.status}</Badge></td>
                      <td className="py-3 px-4 text-gray-400 text-xs" title={u.onboarding_data?.company_description || ''}>{u.onboarding_data?.company_name || '-'}</td>
                      <td className="py-3 px-4 text-gray-400 text-xs">{u.onboarding_data?.industry || '-'}</td>
                      <td className="py-3 px-4 text-gray-400 text-xs">{u.subscription_end_date ? new Date(u.subscription_end_date).toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' }) : u.trial_ends_at ? `Trial: ${new Date(u.trial_ends_at).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' })}` : '-'}</td>
                      <td className="py-3 px-4 text-gray-400 text-xs">{new Date(u.created_at).toLocaleDateString()}</td>
                      <td className="py-3 px-4">
                        {u.role !== 'admin' && (
                          <div className="flex flex-wrap gap-1.5">
                            {u.status === 'active' ? (
                              <>
                                <Button size="sm" variant="outline" onClick={() => handleUpdateUserStatus(u.id, 'disabled')} className="border-red-500 text-red-400 hover:bg-red-900/20 text-xs px-2 py-1 h-7" data-testid={`disable-${u.id}`}><Ban className="w-3 h-3 mr-1" />Disable</Button>
                                <Button size="sm" variant="outline" onClick={() => handleUpdateUserStatus(u.id, 'spam')} className="border-orange-500 text-orange-400 hover:bg-orange-900/20 text-xs px-2 py-1 h-7" data-testid={`spam-${u.id}`}><ShieldAlert className="w-3 h-3 mr-1" />Spam</Button>
                              </>
                            ) : (
                              <Button size="sm" variant="outline" onClick={() => handleUpdateUserStatus(u.id, 'active')} className="border-green-500 text-green-400 hover:bg-green-900/20 text-xs px-2 py-1 h-7" data-testid={`activate-${u.id}`}><Shield className="w-3 h-3 mr-1" />Activate</Button>
                            )}
                            <Button size="sm" variant="outline" onClick={() => handleExtendTrial(u.id)} className="border-blue-500 text-blue-400 hover:bg-blue-900/20 text-xs px-2 py-1 h-7" data-testid={`extend-trial-${u.id}`}><Clock className="w-3 h-3 mr-1" />+7d</Button>
                            <Button size="sm" variant="outline" onClick={() => handleExtendSubscription(u.id, 12)} className="border-purple-500 text-purple-400 hover:bg-purple-900/20 text-xs px-2 py-1 h-7" data-testid={`extend-1y-${u.id}`}>+1Y</Button>
                            <Button size="sm" variant="outline" onClick={() => handleExtendSubscription(u.id, 24)} className="border-pink-500 text-pink-400 hover:bg-pink-900/20 text-xs px-2 py-1 h-7" data-testid={`extend-2y-${u.id}`}>+2Y</Button>
                            <Button size="sm" variant="outline" onClick={() => handleManageCredits(u.id, 'add')} className="border-green-500 text-green-400 hover:bg-green-900/20 text-xs px-2 py-1 h-7" data-testid={`add-credits-${u.id}`}>+Cr</Button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                  {filteredUsers.length === 0 && <tr><td colSpan="10" className="text-center py-8 text-gray-500">No users found</td></tr>}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );};

  const renderTicketsTab = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div><h1 className="text-3xl font-bold text-white mb-2">Support Tickets</h1><p className="text-gray-400">View and respond to user support tickets</p></div>
        <Button variant="outline" size="sm" onClick={fetchTickets} className="border-purple-500 text-purple-400">Refresh</Button>
      </div>
      {tickets.length === 0 ? (
        <Card className="bg-gray-900 border-gray-800"><CardContent className="p-8 text-center text-gray-500">No tickets found</CardContent></Card>
      ) : (
        <div className="space-y-4">
          {tickets.map((t) => (
            <Card key={t.id} className="bg-gray-900 border-gray-800">
              <CardContent className="p-5">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-white font-medium">{t.subject}</h3>
                    <p className="text-gray-500 text-xs mt-1">From: <span className="text-gray-300">{t.user_name}</span> ({t.user_email}) · {new Date(t.created_at).toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge className={t.priority === 'high' ? 'bg-red-900/30 text-red-400' : t.priority === 'medium' ? 'bg-yellow-900/30 text-yellow-400' : 'bg-gray-700 text-gray-300'}>{t.priority}</Badge>
                    <Badge className={t.status === 'open' ? 'bg-yellow-900/30 text-yellow-400' : t.status === 'replied' ? 'bg-blue-900/30 text-blue-400' : 'bg-green-900/30 text-green-400'}>{t.status}</Badge>
                  </div>
                </div>
                <div className="bg-gray-800/50 rounded-lg p-3 mb-3">
                  <p className="text-gray-300 text-sm">{t.message}</p>
                </div>

                {/* Replies */}
                {t.replies && t.replies.length > 0 && (
                  <div className="space-y-2 mb-3">
                    {t.replies.map((r, i) => (
                      <div key={i} className="bg-purple-900/10 border border-purple-800/30 rounded-lg p-3">
                        <p className="text-xs text-purple-400 mb-1">Admin Reply · {r.replied_at ? new Date(r.replied_at).toLocaleDateString('en-IN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : ''}</p>
                        <p className="text-gray-300 text-sm">{r.message}</p>
                      </div>
                    ))}
                  </div>
                )}

                {/* Reply Input */}
                {t.status !== 'closed' && (
                  <div className="flex space-x-2">
                    <Input
                      value={replyText[t.id] || ''}
                      onChange={(e) => setReplyText(prev => ({ ...prev, [t.id]: e.target.value }))}
                      placeholder="Type your reply..."
                      className="bg-gray-800 border-gray-700 text-white text-sm"
                      data-testid={`ticket-reply-input-${t.id}`}
                    />
                    <Button size="sm" onClick={() => handleReplyTicket(t.id)} className="bg-gradient-to-r from-purple-600 to-pink-600" data-testid={`ticket-reply-btn-${t.id}`}><Send className="w-4 h-4" /></Button>
                    <Button size="sm" variant="outline" onClick={() => handleCloseTicket(t.id)} className="border-gray-600 text-gray-400" data-testid={`ticket-close-${t.id}`}><CheckCircle className="w-4 h-4" /></Button>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );

  const renderDataSourcesTab = () => (
    <div className="space-y-6">
      <div><h1 className="text-3xl font-bold text-white mb-2">Data Sources</h1><p className="text-gray-400">Overview of all connected data sources across users</p></div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="p-6 text-center">
            <Database className="w-10 h-10 text-purple-400 mx-auto mb-3" />
            <p className="text-3xl font-bold text-white">{stats.data_sources}</p>
            <p className="text-gray-400 text-sm">Total Connected Sources</p>
          </CardContent>
        </Card>
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="p-6 text-center">
            <Users className="w-10 h-10 text-blue-400 mx-auto mb-3" />
            <p className="text-3xl font-bold text-white">{detailedUsers.filter(u => u.data_sources_count > 0).length}</p>
            <p className="text-gray-400 text-sm">Users with Data Sources</p>
          </CardContent>
        </Card>
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="p-6 text-center">
            <TrendingUp className="w-10 h-10 text-green-400 mx-auto mb-3" />
            <p className="text-3xl font-bold text-white">{detailedUsers.reduce((acc, u) => acc + (u.data_sources_count || 0), 0)}</p>
            <p className="text-gray-400 text-sm">Total User Data Sources</p>
          </CardContent>
        </Card>
      </div>
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader><CardTitle className="text-white">Users by Data Source Count</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-3">
            {detailedUsers.filter(u => u.data_sources_count > 0).map(u => (
              <div key={u.id} className="flex items-center justify-between bg-gray-800/50 rounded-lg p-3">
                <div><p className="text-white">{u.name}</p><p className="text-gray-500 text-xs">{u.email}</p></div>
                <Badge className="bg-purple-900/30 text-purple-400">{u.data_sources_count} sources</Badge>
              </div>
            ))}
            {detailedUsers.filter(u => u.data_sources_count > 0).length === 0 && <p className="text-gray-500 text-center py-4">No users have connected data sources yet.</p>}
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderRevenueTab = () => (
    <div className="space-y-6">
      <div><h1 className="text-3xl font-bold text-white mb-2">Revenue</h1><p className="text-gray-400">Revenue breakdown and trends in INR</p></div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="p-6 text-center">
            <DollarSign className="w-10 h-10 text-green-400 mx-auto mb-3" />
            <p className="text-3xl font-bold text-white">{formatINR(stats.monthly_revenue)}</p>
            <p className="text-gray-400 text-sm">Monthly Revenue</p>
          </CardContent>
        </Card>
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="p-6 text-center">
            <TrendingUp className="w-10 h-10 text-purple-400 mx-auto mb-3" />
            <p className="text-3xl font-bold text-white">{stats.active_subscriptions}</p>
            <p className="text-gray-400 text-sm">Active Subscriptions</p>
          </CardContent>
        </Card>
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="p-6 text-center">
            <Users className="w-10 h-10 text-blue-400 mx-auto mb-3" />
            <p className="text-3xl font-bold text-white">{formatINR(stats.active_subscriptions > 0 ? (stats.monthly_revenue / stats.active_subscriptions).toFixed(0) : 0)}</p>
            <p className="text-gray-400 text-sm">Avg Revenue per User</p>
          </CardContent>
        </Card>
      </div>
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader><CardTitle className="text-white">Revenue Trend (INR)</CardTitle></CardHeader>
        <CardContent>
          {isLoading ? <div className="h-64 flex items-center justify-center text-gray-400">Loading...</div> : (
            <div className="h-64 flex items-end justify-between space-x-3 px-2">
              {revenueData.map((data, i) => {
                const max = Math.max(...revenueData.map(d => d.amount), 1);
                const h = Math.max((data.amount / max) * 100, 4);
                return (
                  <div key={i} className="flex-1 flex flex-col items-center h-full justify-end group">
                    <div className="text-xs text-gray-500 mb-1 opacity-0 group-hover:opacity-100 transition-opacity">{formatINR(data.amount)}</div>
                    <div className="w-full bg-gradient-to-t from-green-600 to-emerald-500 rounded-t-lg hover:from-green-500 hover:to-emerald-400 transition-all min-h-[4px]" style={{ height: `${h}%` }}></div>
                    <span className="text-xs text-gray-500 mt-2">{data.month}</span>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader><CardTitle className="text-white">Revenue by User Plan</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-3">
            {Object.entries(detailedUsers.reduce((acc, u) => { acc[u.plan] = (acc[u.plan] || 0) + 1; return acc; }, {})).map(([plan, count]) => (
              <div key={plan} className="flex items-center justify-between bg-gray-800/50 rounded-lg p-3">
                <span className="text-white">{plan}</span>
                <div className="flex items-center space-x-3">
                  <span className="text-gray-400 text-sm">{count} users</span>
                  <Badge className="bg-purple-900/30 text-purple-400">{plan}</Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderSlackTab = () => (
    <div className="space-y-6">
      <div><h1 className="text-3xl font-bold text-white mb-2">Slack Integration</h1><p className="text-gray-400">Connect your Slack workspace for admin notifications</p></div>
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader><CardTitle className="text-white flex items-center"><MessageSquare className="w-5 h-5 mr-2" /> Slack Connection</CardTitle></CardHeader>
        <CardContent>
          {slackConnected ? (
            <div className="space-y-4">
              <div className="flex items-center space-x-3 bg-green-900/20 border border-green-700 rounded-lg p-4">
                <CheckCircle className="w-6 h-6 text-green-400" />
                <div>
                  <p className="text-white font-medium">Connected to {slackTeam}</p>
                  <p className="text-gray-400 text-sm">Notifications will be sent to your Slack workspace</p>
                </div>
              </div>
              <Button variant="outline" className="border-red-500 text-red-400 hover:bg-red-900/20" onClick={handleDisconnectSlack} data-testid="admin-slack-disconnect">Disconnect Slack</Button>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-gray-400 text-sm">Connect your Slack workspace to receive platform notifications, new user alerts, and revenue updates.</p>
              <div className="space-y-2">
                <label className="text-gray-300 text-sm">Slack Bot Token</label>
                <Input value={slackToken} onChange={(e) => setSlackToken(e.target.value)} placeholder="xoxb-your-bot-token" className="bg-gray-800 border-gray-700 text-white" data-testid="admin-slack-token-input" />
                <p className="text-xs text-gray-500">Create a Slack app at api.slack.com and get a bot token with chat:write and channels:read scopes.</p>
              </div>
              <Button onClick={handleConnectSlack} disabled={!slackToken.trim() || isConnectingSlack} className="bg-gradient-to-r from-purple-600 to-pink-600" data-testid="admin-slack-connect">
                {isConnectingSlack ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <MessageSquare className="w-4 h-4 mr-2" />} Connect Slack
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );

  const renderCouponsTab = () => (
    <div className="space-y-6">
      <div><h1 className="text-3xl font-bold text-white mb-2">Coupon Management</h1><p className="text-gray-400">Create and manage discount coupon codes</p></div>
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader><CardTitle className="text-white flex items-center"><Tag className="w-5 h-5 mr-2" /> Create New Coupon</CardTitle></CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3 items-end">
            <div className="flex-1 min-w-[200px]">
              <label className="text-gray-400 text-sm mb-1 block">Coupon Code</label>
              <Input value={newCouponCode} onChange={(e) => setNewCouponCode(e.target.value)} placeholder="e.g. SAVE20" className="bg-gray-800 border-gray-700 text-white uppercase" data-testid="coupon-code-input" />
            </div>
            <div className="w-32">
              <label className="text-gray-400 text-sm mb-1 block">Discount %</label>
              <Input type="number" min="1" max="100" value={newCouponDiscount} onChange={(e) => setNewCouponDiscount(e.target.value)} placeholder="20" className="bg-gray-800 border-gray-700 text-white" data-testid="coupon-discount-input" />
            </div>
            <Button onClick={handleCreateCoupon} className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700" data-testid="create-coupon-btn"><Plus className="w-4 h-4 mr-1" /> Create</Button>
          </div>
        </CardContent>
      </Card>
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader><CardTitle className="text-white">Active Coupons</CardTitle></CardHeader>
        <CardContent className="p-0">
          {coupons.length === 0 ? (
            <div className="text-center py-8 text-gray-500">No coupons created yet</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead><tr className="border-b border-gray-800">
                  {['Code', 'Discount', 'Status', 'Used', 'Created', 'Actions'].map(h => <th key={h} className="text-left py-3 px-4 text-gray-400 font-medium">{h}</th>)}
                </tr></thead>
                <tbody>
                  {coupons.map((c) => (
                    <tr key={c.id} className="border-b border-gray-800 hover:bg-gray-800/50">
                      <td className="py-3 px-4 text-white font-mono font-bold" data-testid={`coupon-row-${c.code}`}>{c.code}</td>
                      <td className="py-3 px-4 text-green-400 font-bold">{c.discount_percentage}%</td>
                      <td className="py-3 px-4"><Badge className={c.is_active ? 'bg-green-900/30 text-green-400 border-green-700' : 'bg-red-900/30 text-red-400 border-red-700'}>{c.is_active ? 'Active' : 'Inactive'}</Badge></td>
                      <td className="py-3 px-4 text-gray-400">{c.usage_count}x</td>
                      <td className="py-3 px-4 text-gray-400 text-xs">{new Date(c.created_at).toLocaleDateString()}</td>
                      <td className="py-3 px-4">
                        <div className="flex gap-2">
                          <Button size="sm" variant="outline" onClick={() => handleToggleCoupon(c.id)} className={c.is_active ? 'border-yellow-500 text-yellow-400 hover:bg-yellow-900/20' : 'border-green-500 text-green-400 hover:bg-green-900/20'} data-testid={`toggle-coupon-${c.id}`}>
                            {c.is_active ? <><ToggleRight className="w-3 h-3 mr-1" />Disable</> : <><ToggleLeft className="w-3 h-3 mr-1" />Enable</>}
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => handleDeleteCoupon(c.id)} className="border-red-500 text-red-400 hover:bg-red-900/20" data-testid={`delete-coupon-${c.id}`}><Trash2 className="w-3 h-3" /></Button>
                        </div>
                      </td>
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

  const renderContent = () => {
    switch (activeTab) {
      case 'users': return renderUsersTab();
      case 'tickets': return renderTicketsTab();
      case 'coupons': return renderCouponsTab();
      case 'datasources': return renderDataSourcesTab();
      case 'revenue': return renderRevenueTab();
      case 'slack': return renderSlackTab();
      default: return renderDashboardTab();
    }
  };

  return (
    <div className="min-h-screen bg-gray-950">
      <nav className="bg-gray-900 border-b border-gray-800 sticky top-0 z-40">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button className="lg:hidden text-gray-400 hover:text-white" onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
                {isSidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
              <div className="flex items-center space-x-2">
                <img src="/analiyx-logo.jpg" alt="Analiyx" className="h-8 object-contain" />
                <span className="text-sm font-medium text-gray-400">Admin</span>
              </div>
            </div>
            <Button variant="ghost" className="text-gray-400 hover:text-white" onClick={handleLogout} data-testid="admin-logout-button"><LogOut className="w-5 h-5 mr-2" /> Logout</Button>
          </div>
        </div>
      </nav>

      <div className="flex">
        <aside className={`${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-30 w-64 bg-gray-900 border-r border-gray-800 transition-transform duration-300 mt-16 lg:mt-0`}>
          <div className="p-6 space-y-2">
            {sidebarItems.map(item => (
              <Button key={item.id} variant="ghost" className={`w-full justify-start ${activeTab === item.id ? 'text-purple-400 bg-purple-900/20' : 'text-gray-400 hover:text-white'}`}
                onClick={() => { setActiveTab(item.id); setIsSidebarOpen(false); }} data-testid={`admin-tab-${item.id}`}>
                <item.icon className="w-5 h-5 mr-3" /> {item.label}
              </Button>
            ))}
          </div>
        </aside>
        <main className="flex-1 p-6 lg:p-8"><div className="max-w-7xl mx-auto">{renderContent()}</div></main>
      </div>
    </div>
  );
};

export default AdminDashboard;
