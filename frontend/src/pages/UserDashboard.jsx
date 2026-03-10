import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { useNavigate } from 'react-router-dom';
import { Sparkles, LogOut, Database, CreditCard, TrendingUp, X, ArrowUp, ArrowDown, Minus, Brain, Facebook, Megaphone, BarChart, BookOpen, Upload, FileSpreadsheet, CheckCircle, Loader2, Download } from 'lucide-react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { integrations, connectedSources, aiVisibilityInsights } from '../mock/mockData';
import { dataSourceAPI } from '../services/api';
import { toast } from '../hooks/use-toast';

const UserDashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [isDataSourceModalOpen, setIsDataSourceModalOpen] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [fileDetails, setFileDetails] = useState(null);
  const [showFileDetails, setShowFileDetails] = useState(false);

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
    fetchUploadedFiles();
  }, [navigate]);

  const fetchUploadedFiles = async () => {
    try {
      const data = await dataSourceAPI.getUploadedFiles();
      setUploadedFiles(data.files || []);
    } catch (error) {
      console.error('Error fetching files:', error);
    }
  };

  const handleViewFileDetails = async (fileId) => {
    try {
      const details = await dataSourceAPI.getFileDetails(fileId);
      setFileDetails(details);
      setShowFileDetails(true);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load file details',
        variant: 'destructive'
      });
    }
  };

  const handleDownloadReport = () => {
    toast({
      title: 'Report Download',
      description: 'Report download will start shortly...',
    });
    // Will implement actual download
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      const validTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
      if (!validTypes.includes(file.type) && !file.name.match(/\.(csv|xlsx|xls)$/i)) {
        toast({
          title: 'Invalid file type',
          description: 'Please upload CSV or Excel files only.',
          variant: 'destructive'
        });
        return;
      }
      setSelectedFile(file);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    try {
      const result = await dataSourceAPI.uploadFile(selectedFile);
      
      toast({
        title: 'File uploaded successfully!',
        description: result.message,
      });
      
      setSelectedFile(null);
      setShowFileUpload(false);
      setIsDataSourceModalOpen(false);
      fetchUploadedFiles();
      
    } catch (error) {
      toast({
        title: 'Upload failed',
        description: error.response?.data?.detail || 'Failed to upload file',
        variant: 'destructive'
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleIntegrationClick = async (integration) => {
    if (integration.name === 'Excel' || integration.name === 'CSV') {
      setShowFileUpload(true);
    } else if (integration.name === 'Google Ads' || integration.name === 'Meta Ads') {
      // Trigger OAuth flow
      try {
        const integrationKey = integration.name === 'Google Ads' ? 'google_ads' : 'meta_ads';
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/integrations/oauth/authorize/${integrationKey}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        const data = await response.json();
        
        // Redirect to OAuth URL
        window.location.href = data.authorization_url;
      } catch (error) {
        toast({
          title: 'Connection failed',
          description: 'Failed to start OAuth flow. Please try again.',
          variant: 'destructive'
        });
      }
    } else {
      toast({
        title: 'Coming Soon',
        description: `${integration.name} integration will be available soon!`,
      });
    }
  };

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

        {/* Uploaded Files Section */}
        {uploadedFiles.length > 0 && (
          <Card className="bg-gray-900 border-gray-800 mb-6">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-white flex items-center">
                  <FileSpreadsheet className="w-5 h-5 mr-2" />
                  Your Uploaded Files
                </CardTitle>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleDownloadReport}
                  className="border-purple-500 text-purple-400 hover:bg-purple-900/20"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download All Reports
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {uploadedFiles.map((file) => (
                  <div 
                    key={file.id}
                    className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition-colors cursor-pointer"
                    onClick={() => handleViewFileDetails(file.id)}
                  >
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 bg-green-900/20 rounded-lg flex items-center justify-center">
                        <CheckCircle className="w-5 h-5 text-green-500" />
                      </div>
                      <div>
                        <p className="text-white font-medium">{file.filename}</p>
                        <p className="text-gray-400 text-sm">
                          {file.total_rows} rows × {file.total_columns} columns • Uploaded {file.uploaded_at}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className="px-3 py-1 bg-green-900/20 text-green-400 text-xs rounded-full border border-green-700">
                        {file.status}
                      </span>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-purple-400 hover:text-purple-300"
                      >
                        View Analytics →
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

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
            <DialogTitle className="text-2xl font-bold">
              {showFileUpload ? 'Upload File' : 'Connect Data Source'}
            </DialogTitle>
            <DialogDescription className="text-gray-400">
              {showFileUpload 
                ? 'Upload your CSV or Excel file to analyze data'
                : 'Choose a data source to connect and start analyzing your data'}
            </DialogDescription>
          </DialogHeader>
          
          {showFileUpload ? (
            <div className="py-6">
              <div className="border-2 border-dashed border-gray-700 rounded-xl p-8 text-center hover:border-purple-500 transition-colors">
                <input
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleFileSelect}
                  className="hidden"
                  id="file-upload"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-white font-semibold mb-2">
                    {selectedFile ? selectedFile.name : 'Click to upload or drag and drop'}
                  </p>
                  <p className="text-gray-400 text-sm">CSV or Excel files (max 10MB)</p>
                </label>
              </div>

              {selectedFile && (
                <div className="mt-4 bg-gray-800 rounded-lg p-4 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <FileSpreadsheet className="w-8 h-8 text-green-500" />
                    <div>
                      <p className="text-white font-medium">{selectedFile.name}</p>
                      <p className="text-gray-400 text-sm">
                        {(selectedFile.size / 1024).toFixed(2)} KB
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedFile(null)}
                    className="text-gray-400 hover:text-white"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              )}

              <div className="flex space-x-3 mt-6">
                <Button
                  variant="outline"
                  className="flex-1 border-gray-700 text-gray-300 hover:bg-gray-800"
                  onClick={() => {
                    setShowFileUpload(false);
                    setSelectedFile(null);
                  }}
                >
                  Back
                </Button>
                <Button
                  className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                  onClick={handleFileUpload}
                  disabled={!selectedFile || isUploading}
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4 mr-2" />
                      Upload & Analyze
                    </>
                  )}
                </Button>
              </div>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 py-4">
                {integrations.map((integration, index) => (
                  <button
                    key={index}
                    className="group relative bg-gray-800 border border-gray-700 rounded-xl p-4 hover:border-purple-500 transition-all duration-300 transform hover:scale-105 hover:shadow-xl hover:shadow-purple-500/20"
                    onClick={() => handleIntegrationClick(integration)}
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
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default UserDashboard;
