import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { adminAPI } from '../services/api';
import { Users, DollarSign, Database, TrendingUp, ArrowUp, ArrowDown, LogOut, Sparkles, Menu, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Badge } from '../components/ui/badge';

const iconMap = {
  'Total Users': Users,
  'Active Subscriptions': TrendingUp,
  'Monthly Revenue': DollarSign,
  'Data Sources': Database
};

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [stats, setStats] = useState({
    total_users: 0,
    active_subscriptions: 0,
    monthly_revenue: 0,
    data_sources: 0
  });
  const [users, setUsers] = useState([]);
  const [userGrowthData, setUserGrowthData] = useState([]);
  const [revenueData, setRevenueData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      
      // Fetch all data in parallel
      const [statsData, usersData, userGrowth, revenue] = await Promise.all([
        adminAPI.getStats(),
        adminAPI.getUsers(1, 5),
        adminAPI.getUserGrowth(),
        adminAPI.getRevenue()
      ]);
      
      setStats(statsData);
      setUsers(usersData.users);
      setUserGrowthData(userGrowth.data);
      setRevenueData(revenue.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      // If unauthorized, redirect to login
      if (error.response?.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        navigate('/login');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const adminStatsDisplay = [
    { label: 'Total Users', value: stats.total_users.toLocaleString(), change: '+12.5%', trend: 'up' },
    { label: 'Active Subscriptions', value: stats.active_subscriptions.toLocaleString(), change: '+8.2%', trend: 'up' },
    { label: 'Monthly Revenue', value: `$${stats.monthly_revenue.toLocaleString()}`, change: '+15.3%', trend: 'up' },
    { label: 'Data Sources', value: stats.data_sources.toLocaleString(), change: '+22.1%', trend: 'up' }
  ];

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Top Navigation */}
      <nav className="bg-gray-900 border-b border-gray-800 sticky top-0 z-40">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                className="lg:hidden text-gray-400 hover:text-white"
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              >
                {isSidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold text-white">Papermap Admin</span>
              </div>
            </div>
            <Button
              variant="ghost"
              className="text-gray-400 hover:text-white"
              onClick={handleLogout}
            >
              <LogOut className="w-5 h-5 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </nav>

      <div className="flex">
        {/* Sidebar */}
        <aside className={`${
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-30 w-64 bg-gray-900 border-r border-gray-800 transition-transform duration-300 ease-in-out mt-16 lg:mt-0`}>
          <div className="p-6 space-y-2">
            <Button variant="ghost" className="w-full justify-start text-purple-400 bg-purple-900/20">
              <TrendingUp className="w-5 h-5 mr-3" />
              Dashboard
            </Button>
            <Button variant="ghost" className="w-full justify-start text-gray-400 hover:text-white">
              <Users className="w-5 h-5 mr-3" />
              Users
            </Button>
            <Button variant="ghost" className="w-full justify-start text-gray-400 hover:text-white">
              <Database className="w-5 h-5 mr-3" />
              Data Sources
            </Button>
            <Button variant="ghost" className="w-full justify-start text-gray-400 hover:text-white">
              <DollarSign className="w-5 h-5 mr-3" />
              Revenue
            </Button>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6 lg:p-8">
          <div className="max-w-7xl mx-auto space-y-8">
            {/* Header */}
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">Dashboard Overview</h1>
              <p className="text-gray-400">Monitor your platform's key metrics and performance</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {adminStatsDisplay.map((stat, index) => {
                const Icon = iconMap[stat.label];
                const isPositive = stat.trend === 'up';
                return (
                  <Card key={index} className="bg-gray-900 border-gray-800 hover:border-purple-500/50 transition-all duration-300">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div className="p-3 bg-purple-900/20 rounded-lg">
                          <Icon className="w-6 h-6 text-purple-400" />
                        </div>
                        <div className={`flex items-center text-sm font-semibold ${
                          isPositive ? 'text-green-500' : 'text-red-500'
                        }`}>
                          {isPositive ? <ArrowUp className="w-4 h-4 mr-1" /> : <ArrowDown className="w-4 h-4 mr-1" />}
                          {stat.change}
                        </div>
                      </div>
                      <div>
                        <p className="text-gray-400 text-sm mb-1">{stat.label}</p>
                        <p className="text-3xl font-bold text-white">{stat.value}</p>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* User Growth Chart */}
              <Card className="bg-gray-900 border-gray-800">
                <CardHeader>
                  <CardTitle className="text-white">User Growth</CardTitle>
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <div className="h-64 flex items-center justify-center text-gray-400">Loading...</div>
                  ) : (
                    <div className="h-64 flex items-end justify-between space-x-2">
                      {userGrowthData.map((data, index) => {
                        const maxValue = Math.max(...userGrowthData.map(d => d.users));
                        const height = (data.users / maxValue) * 100;
                        return (
                          <div key={index} className="flex-1 flex flex-col items-center">
                            <div className="w-full bg-gradient-to-t from-purple-600 to-pink-600 rounded-t-lg transition-all duration-300 hover:from-purple-500 hover:to-pink-500" style={{ height: `${height}%` }}></div>
                            <span className="text-xs text-gray-500 mt-2">{data.month}</span>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Revenue Chart */}
              <Card className="bg-gray-900 border-gray-800">
                <CardHeader>
                  <CardTitle className="text-white">Revenue Trend</CardTitle>
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <div className="h-64 flex items-center justify-center text-gray-400">Loading...</div>
                  ) : (
                    <div className="h-64 flex items-end justify-between space-x-2">
                      {revenueData.map((data, index) => {
                        const maxValue = Math.max(...revenueData.map(d => d.amount));
                        const height = (data.amount / maxValue) * 100;
                        return (
                          <div key={index} className="flex-1 flex flex-col items-center">
                            <div className="w-full bg-gradient-to-t from-green-600 to-emerald-600 rounded-t-lg transition-all duration-300 hover:from-green-500 hover:to-emerald-500" style={{ height: `${height}%` }}></div>
                            <span className="text-xs text-gray-500 mt-2">{data.month}</span>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Recent Users Table */}
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader>
                <CardTitle className="text-white">Recent Users</CardTitle>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="text-center py-8 text-gray-400">Loading users...</div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-gray-800">
                          <th className="text-left py-3 px-4 text-gray-400 font-medium">Name</th>
                          <th className="text-left py-3 px-4 text-gray-400 font-medium">Email</th>
                          <th className="text-left py-3 px-4 text-gray-400 font-medium">Plan</th>
                          <th className="text-left py-3 px-4 text-gray-400 font-medium">Status</th>
                          <th className="text-left py-3 px-4 text-gray-400 font-medium">Joined</th>
                        </tr>
                      </thead>
                      <tbody>
                        {users.map((user) => (
                          <tr key={user.id} className="border-b border-gray-800 hover:bg-gray-800/50 transition-colors">
                            <td className="py-3 px-4 text-white">{user.name}</td>
                            <td className="py-3 px-4 text-gray-400">{user.email}</td>
                            <td className="py-3 px-4">
                              <Badge variant="secondary" className="bg-purple-900/30 text-purple-400 border-purple-700">
                                {user.plan}
                              </Badge>
                            </td>
                            <td className="py-3 px-4">
                              <Badge className={user.status === 'active' ? 'bg-green-900/30 text-green-400 border-green-700' : 'bg-gray-700/30 text-gray-400 border-gray-600'}>
                                {user.status}
                              </Badge>
                            </td>
                            <td className="py-3 px-4 text-gray-400">{user.joined}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
};

export default AdminDashboard;