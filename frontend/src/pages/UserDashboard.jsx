import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { useNavigate } from 'react-router-dom';
import { Sparkles, LogOut, Database, CreditCard, TrendingUp, X, ArrowUp, ArrowDown, Minus, Brain, Facebook, Megaphone, BarChart, BookOpen } from 'lucide-react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { integrations, connectedSources, aiVisibilityInsights } from '../mock/mockData';

const UserDashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [isDataSourceModalOpen, setIsDataSourceModalOpen] = useState(false);

  useEffect(() => {
    // Check if user is logged in
    const userData = localStorage.getItem('user');
    if (!userData) {
      navigate('/login');
      return;
    }

    const parsedUser = JSON.parse(userData);
    
    // If admin, redirect to admin panel
    if (parsedUser.role === 'admin') {
      navigate('/admin');
      return;
    }

    setUser(parsedUser);
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-gray-400">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Top Navigation */}
      <nav className="bg-gray-900 border-b border-gray-800 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white">Analiyx</span>
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

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Welcome, {user.name}!</h1>
          <p className="text-gray-400">Manage your data analytics and subscriptions</p>
        </div>

        {/* User Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-gray-900 border-gray-800">
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-purple-900/20 rounded-lg">
                  <CreditCard className="w-6 h-6 text-purple-400" />
                </div>
                <div>
                  <p className="text-gray-400 text-sm">Current Plan</p>
                  <p className="text-xl font-bold text-white">{user.plan}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-900 border-gray-800">
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-green-900/20 rounded-lg">
                  <TrendingUp className="w-6 h-6 text-green-400" />
                </div>
                <div>
                  <p className="text-gray-400 text-sm">Credits Available</p>
                  <p className="text-xl font-bold text-white">{user.credits}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-900 border-gray-800">
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-blue-900/20 rounded-lg">
                  <Database className="w-6 h-6 text-blue-400" />
                </div>
                <div>
                  <p className="text-gray-400 text-sm">Account Status</p>
                  <p className="text-xl font-bold text-white capitalize">{user.status}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Dashboard Content - Connected Data Sources Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {connectedSources.map((source) => {
            const iconMap = {
              brain: Brain,
              facebook: Facebook,
              megaphone: Megaphone,
              'bar-chart': BarChart,
              'book-open': BookOpen
            };
            const Icon = iconMap[source.icon] || Database;

            return (
              <Card key={source.id} className="bg-gray-900 border-gray-800">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div 
                        className="w-10 h-10 rounded-lg flex items-center justify-center"
                        style={{ backgroundColor: `${source.color}20` }}
                      >
                        <Icon className="w-5 h-5" style={{ color: source.color }} />
                      </div>
                      <div>
                        <CardTitle className="text-white text-lg">{source.name}</CardTitle>
                        <p className="text-xs text-gray-500">Last synced: {source.lastSync}</p>
                      </div>
                    </div>
                    <span className="px-2 py-1 bg-green-900/20 text-green-400 text-xs rounded-full border border-green-700">
                      {source.status}
                    </span>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    {Object.entries(source.metrics).map(([key, value], index) => (
                      <div key={index} className="bg-gray-800/50 rounded-lg p-3">
                        <p className="text-gray-400 text-xs capitalize mb-1">
                          {key.replace(/([A-Z])/g, ' $1').trim()}
                        </p>
                        <p className="text-white font-semibold">{value}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* AI Visibility Detailed Insights */}
        <Card className="bg-gray-900 border-gray-800 mt-6">
          <CardHeader>
            <CardTitle className="text-white">AI Visibility Insights</CardTitle>
            <p className="text-gray-400 text-sm">Your brand's presence across AI platforms</p>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {aiVisibilityInsights.map((insight, index) => {
                const trendIcons = {
                  up: <ArrowUp className="w-4 h-4 text-green-500" />,
                  down: <ArrowDown className="w-4 h-4 text-red-500" />,
                  neutral: <Minus className="w-4 h-4 text-gray-500" />
                };

                return (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition-colors">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-purple-900/20 rounded-lg flex items-center justify-center">
                        <Brain className="w-6 h-6 text-purple-400" />
                      </div>
                      <div>
                        <p className="text-white font-semibold">{insight.platform}</p>
                        <p className="text-gray-400 text-sm">{insight.appearances} appearances</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <span className="text-gray-400 text-sm">{insight.ranking}</span>
                      {trendIcons[insight.trend]}
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Connect More Sources CTA */}
        <Card className="bg-gradient-to-br from-purple-900/20 to-pink-900/20 border-purple-500/30 mt-6">
          <CardContent className="p-8 text-center">
            <Sparkles className="w-12 h-12 text-purple-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">
              Connect More Data Sources
            </h3>
            <p className="text-gray-400 mb-6">
              Get deeper insights by connecting all your business data sources
            </p>
            <Button 
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white"
              onClick={() => setIsDataSourceModalOpen(true)}
            >
              Browse Integrations
            </Button>
          </CardContent>
        </Card>
      </main>

      {/* Data Source Connection Modal */}
      <Dialog open={isDataSourceModalOpen} onOpenChange={setIsDataSourceModalOpen}>
        <DialogContent className="bg-gray-900 border-gray-800 text-white max-w-3xl">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold">Connect Data Source</DialogTitle>
            <DialogDescription className="text-gray-400">
              Choose a data source to connect and start analyzing your data
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 py-4">
            {integrations.map((integration, index) => (
              <button
                key={index}
                className="group relative bg-gray-800 border border-gray-700 rounded-xl p-4 hover:border-purple-500 transition-all duration-300 transform hover:scale-105 hover:shadow-xl hover:shadow-purple-500/20"
                onClick={() => {
                  // TODO: Implement actual data source connection
                  alert(`Connecting to ${integration.name}...`);
                  setIsDataSourceModalOpen(false);
                }}
              >
                <div className="flex flex-col items-center space-y-2">
                  <div 
                    className="w-12 h-12 rounded-lg flex items-center justify-center"
                    style={{ backgroundColor: `${integration.color}20` }}
                  >
                    <Database className="w-6 h-6" style={{ color: integration.color }} />
                  </div>
                  <span className="text-xs text-gray-400 text-center group-hover:text-white transition-colors">
                    {integration.name}
                  </span>
                </div>
              </button>
            ))}
          </div>

          <div className="pt-4 border-t border-gray-800">
            <p className="text-sm text-gray-400 text-center">
              Don't see your data source? <span className="text-purple-400 cursor-pointer hover:underline">Contact support</span>
            </p>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default UserDashboard;
