import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { adminAPI } from '../services/api';
import { Users, DollarSign, Database, TrendingUp, ArrowUp, ArrowDown, LogOut, Sparkles, Menu, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Badge } from '../components/ui/badge';
import { toast } from '../hooks/use-toast';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState({ total_users: 0, active_subscriptions: 0, monthly_revenue: 0, data_sources: 0 });
  const [detailedUsers, setDetailedUsers] = useState([]);
  const [userGrowthData, setUserGrowthData] = useState([]);
  const [revenueData, setRevenueData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    const token = localStorage.getItem('token');
    if (!userData || !token) { navigate('/login'); return; }
    try {
      const parsed = JSON.parse(userData);
      const isAdmin = parsed.role === 'admin' || parsed.email === 'admin@papermap.com' || parsed.email === 'admin@analiyx.com';
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
    } catch (error) {
      if (error.response?.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        navigate('/login');
      }
    } finally { setIsLoading(false); }
  };

  const handleToggleUserStatus = async (userId, currentStatus) => {
    try {
      const newStatus = currentStatus === 'active' ? 'inactive' : 'active';
      await adminAPI.updateUserStatus(userId, newStatus);
      const data = await adminAPI.getAllUsersDetails();
      setDetailedUsers(data.users || []);
      toast({ title: 'Success', description: `User ${newStatus === 'active' ? 'enabled' : 'disabled'}.` });
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

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const sidebarItems = [
    { id: 'dashboard', label: 'Dashboard', icon: TrendingUp },
    { id: 'users', label: 'Users', icon: Users },
    { id: 'datasources', label: 'Data Sources', icon: Database },
    { id: 'revenue', label: 'Revenue', icon: DollarSign },
  ];

  const formatINR = (amount) => `₹${Number(amount).toLocaleString('en-IN')}`;

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
              <div className="h-64 flex items-end justify-between space-x-2">
                {userGrowthData.map((data, i) => {
                  const max = Math.max(...userGrowthData.map(d => d.users), 1);
                  const h = (data.users / max) * 100;
                  return (<div key={i} className="flex-1 flex flex-col items-center"><div className="w-full bg-gradient-to-t from-purple-600 to-pink-600 rounded-t-lg hover:from-purple-500 hover:to-pink-500 transition-all" style={{ height: `${h}%` }}></div><span className="text-xs text-gray-500 mt-2">{data.month}</span></div>);
                })}
              </div>
            )}
          </CardContent>
        </Card>
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader><CardTitle className="text-white">Revenue Trend (INR)</CardTitle></CardHeader>
          <CardContent>
            {isLoading ? <div className="h-64 flex items-center justify-center text-gray-400">Loading...</div> : (
              <div className="h-64 flex items-end justify-between space-x-2">
                {revenueData.map((data, i) => {
                  const max = Math.max(...revenueData.map(d => d.amount), 1);
                  const h = (data.amount / max) * 100;
                  return (<div key={i} className="flex-1 flex flex-col items-center"><div className="w-full bg-gradient-to-t from-green-600 to-emerald-600 rounded-t-lg hover:from-green-500 hover:to-emerald-500 transition-all" style={{ height: `${h}%` }}></div><span className="text-xs text-gray-500 mt-2">{data.month}</span></div>);
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );

  const renderUsersTab = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div><h1 className="text-3xl font-bold text-white mb-2">User Management</h1><p className="text-gray-400">Manage all registered users</p></div>
        <Button variant="outline" size="sm" onClick={fetchDashboardData} className="border-purple-500 text-purple-400">Refresh</Button>
      </div>
      <Card className="bg-gray-900 border-gray-800">
        <CardContent className="p-0">
          {isLoading ? <div className="text-center py-8 text-gray-400">Loading...</div> : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead><tr className="border-b border-gray-800">
                  {['Name', 'Email', 'Plan', 'Credits', 'Role', 'Status', 'Joined', 'Actions'].map(h => <th key={h} className="text-left py-3 px-4 text-gray-400 font-medium">{h}</th>)}
                </tr></thead>
                <tbody>
                  {detailedUsers.map((u) => (
                    <tr key={u.id} className="border-b border-gray-800 hover:bg-gray-800/50">
                      <td className="py-3 px-4 text-white">{u.name}</td>
                      <td className="py-3 px-4 text-gray-400">{u.email}</td>
                      <td className="py-3 px-4"><Badge variant="secondary" className="bg-purple-900/30 text-purple-400 border-purple-700">{u.plan}</Badge></td>
                      <td className="py-3 px-4 text-white">{u.credits}</td>
                      <td className="py-3 px-4"><Badge className={u.role === 'admin' ? 'bg-yellow-900/30 text-yellow-400 border-yellow-700' : 'bg-gray-700 text-gray-300'}>{u.role}</Badge></td>
                      <td className="py-3 px-4"><Badge className={u.status === 'active' ? 'bg-green-900/30 text-green-400 border-green-700' : 'bg-red-900/30 text-red-400 border-red-700'}>{u.status}</Badge></td>
                      <td className="py-3 px-4 text-gray-400">{new Date(u.created_at).toLocaleDateString()}</td>
                      <td className="py-3 px-4">
                        <div className="flex space-x-2">
                          <Button size="sm" variant="outline" onClick={() => handleToggleUserStatus(u.id, u.status)} className={u.status === 'active' ? 'border-red-500 text-red-400 hover:bg-red-900/20' : 'border-green-500 text-green-400 hover:bg-green-900/20'} data-testid={`toggle-status-${u.id}`}>
                            {u.status === 'active' ? 'Disable' : 'Enable'}
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => handleExtendTrial(u.id)} className="border-blue-500 text-blue-400 hover:bg-blue-900/20" data-testid={`extend-trial-${u.id}`}>+7 Days</Button>
                          <Button size="sm" variant="outline" onClick={() => handleManageCredits(u.id, 'add')} className="border-green-500 text-green-400 hover:bg-green-900/20" data-testid={`add-credits-${u.id}`}>+ Credits</Button>
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
      {/* Users with sources */}
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
      {/* Revenue Chart */}
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader><CardTitle className="text-white">Revenue Trend (INR)</CardTitle></CardHeader>
        <CardContent>
          {isLoading ? <div className="h-64 flex items-center justify-center text-gray-400">Loading...</div> : (
            <div className="h-64 flex items-end justify-between space-x-3">
              {revenueData.map((data, i) => {
                const max = Math.max(...revenueData.map(d => d.amount), 1);
                const h = (data.amount / max) * 100;
                return (
                  <div key={i} className="flex-1 flex flex-col items-center group">
                    <div className="text-xs text-gray-500 mb-1 opacity-0 group-hover:opacity-100 transition-opacity">{formatINR(data.amount)}</div>
                    <div className="w-full bg-gradient-to-t from-green-600 to-emerald-500 rounded-t-lg hover:from-green-500 hover:to-emerald-400 transition-all" style={{ height: `${h}%` }}></div>
                    <span className="text-xs text-gray-500 mt-2">{data.month}</span>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
      {/* Revenue by Plan */}
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

  const renderContent = () => {
    switch (activeTab) {
      case 'users': return renderUsersTab();
      case 'datasources': return renderDataSourcesTab();
      case 'revenue': return renderRevenueTab();
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
                <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center"><Sparkles className="w-5 h-5 text-white" /></div>
                <span className="text-xl font-bold text-white">Analiyx Admin</span>
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
