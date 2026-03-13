import React, { useEffect, useState, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Sparkles, LogOut, Database, CreditCard, TrendingUp, X, ArrowUp, ArrowDown, Minus, Brain, Facebook, Megaphone, BarChart, BookOpen, Upload, FileSpreadsheet, CheckCircle, Loader2, Download, Clock, AlertTriangle, Plus, Folder, MessageSquare, Send, Mail, Globe, Search, Zap, Hash } from 'lucide-react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { integrations } from '../mock/mockData';
import { dataSourceAPI, workspaceAPI, supportAPI, authAPI } from '../services/api';
import { toast } from '../hooks/use-toast';
import { downloadComprehensiveReport, exportFilesToExcel } from '../utils/reportExport';
import api from '../services/api';

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
  const [trialDaysLeft, setTrialDaysLeft] = useState(null);
  const [trialExpired, setTrialExpired] = useState(false);
  const [showWorkspaceModal, setShowWorkspaceModal] = useState(false);
  const [workspaces, setWorkspaces] = useState([]);
  const [newWorkspace, setNewWorkspace] = useState({ name: '', dataSources: [] });
  const [showSupportModal, setShowSupportModal] = useState(false);
  const [ticketForm, setTicketForm] = useState({ subject: '', message: '', priority: 'medium' });
  const [tickets, setTickets] = useState([]);
  const [showAIVisibility, setShowAIVisibility] = useState(false);
  const [aiUrl, setAiUrl] = useState('');
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [isProcessingPayment, setIsProcessingPayment] = useState(false);
  const [searchParams] = useSearchParams();
  const [slackConnected, setSlackConnected] = useState(false);
  const [slackTeam, setSlackTeam] = useState('');
  const [slackChannels, setSlackChannels] = useState([]);
  const [showSlackPanel, setShowSlackPanel] = useState(false);
  const [slackToken, setSlackToken] = useState('');
  const [isConnectingSlack, setIsConnectingSlack] = useState(false);
  const [slackMessage, setSlackMessage] = useState('');
  const [selectedChannel, setSelectedChannel] = useState('');

  const refreshUser = useCallback(async () => {
    try {
      const userData = await authAPI.getCurrentUser();
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
      calculateTrialDays(userData);
    } catch {
      // use cached
    }
  }, []);

  const calculateTrialDays = (userData) => {
    if (userData.trial_ends_at) {
      const endDate = new Date(userData.trial_ends_at);
      const now = new Date();
      const diffMs = endDate - now;
      const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
      if (diffDays <= 0) {
        setTrialExpired(true);
        setTrialDaysLeft(0);
      } else {
        setTrialDaysLeft(diffDays);
        setTrialExpired(false);
      }
    }
  };

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (!userData) { navigate('/login'); return; }
    const parsed = JSON.parse(userData);
    if (parsed.role === 'admin') { navigate('/admin'); return; }
    setUser(parsed);
    calculateTrialDays(parsed);
    fetchUploadedFiles();
    fetchWorkspaces();
    fetchTickets();
    fetchSlackStatus();
    refreshUser();
  }, [navigate, refreshUser]);

  const fetchUploadedFiles = async () => {
    try {
      const data = await dataSourceAPI.getUploadedFiles();
      setUploadedFiles(data.files || []);
    } catch (error) { console.error('Error fetching files:', error); }
  };

  const fetchWorkspaces = async () => {
    try {
      const data = await workspaceAPI.list();
      setWorkspaces(data.workspaces || []);
    } catch (error) { console.error('Error fetching workspaces:', error); }
  };

  const fetchTickets = async () => {
    try {
      const data = await supportAPI.getTickets();
      setTickets(data.tickets || []);
    } catch (error) { console.error('Error fetching tickets:', error); }
  };

  const handleViewFileDetails = async (fileId) => {
    try {
      const details = await dataSourceAPI.getFileDetails(fileId);
      setFileDetails(details);
      setShowFileDetails(true);
    } catch {
      toast({ title: 'Error', description: 'Failed to load file details', variant: 'destructive' });
    }
  };

  const handleDownloadReport = async () => {
    try {
      if (!uploadedFiles || uploadedFiles.length === 0) {
        toast({ title: 'No Data', description: 'Upload files first to generate a report.', variant: 'destructive' });
        return;
      }
      // Direct Excel download — no confirm dialog
      exportFilesToExcel(uploadedFiles, null);
      toast({ title: 'Report Downloaded!', description: 'Excel report saved to your device.' });
    } catch (err) {
      console.error('Download error:', err);
      toast({ title: 'Download Failed', description: String(err.message || err), variant: 'destructive' });
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.name.match(/\.(csv|xlsx|xls)$/i)) {
        toast({ title: 'Invalid file type', description: 'Please upload CSV or Excel files only.', variant: 'destructive' });
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
      toast({ title: 'File uploaded successfully!', description: result.message });
      setSelectedFile(null);
      setShowFileUpload(false);
      setIsDataSourceModalOpen(false);
      fetchUploadedFiles();
    } catch (error) {
      const detail = error.response?.data?.detail || '';
      if (detail.includes('DATA_SOURCE_LIMIT_REACHED')) {
        setIsDataSourceModalOpen(false);
        setShowFileUpload(false);
        setShowUpgradeModal(true);
        toast({ title: 'Data Source Limit Reached', description: 'Upgrade to Business Pro for unlimited data source connections.', variant: 'destructive' });
      } else {
        toast({ title: 'Upload failed', description: detail || 'Failed to upload file', variant: 'destructive' });
      }
    } finally { setIsUploading(false); }
  };

  const handleIntegrationClick = async (integration) => {
    if (integration.name === 'Excel' || integration.name === 'CSV') {
      setShowFileUpload(true);
    } else if (integration.name === 'Google Ads' || integration.name === 'Meta Ads') {
      try {
        const integrationKey = integration.name === 'Google Ads' ? 'google_ads' : 'meta_ads';
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/integrations/oauth/authorize/${integrationKey}`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const data = await response.json();
        if (data.authorization_url) window.location.href = data.authorization_url;
      } catch {
        toast({ title: 'Connection failed', description: 'Failed to start OAuth flow.', variant: 'destructive' });
      }
    } else {
      toast({ title: 'Coming Soon', description: `${integration.name} integration will be available soon!` });
    }
  };

  const handleCreateWorkspace = async () => {
    if (!newWorkspace.name.trim()) return;
    try {
      await workspaceAPI.create(newWorkspace.name, newWorkspace.dataSources);
      toast({ title: 'Workspace Created!', description: `'${newWorkspace.name}' is ready.` });
      setShowWorkspaceModal(false);
      setNewWorkspace({ name: '', dataSources: [] });
      fetchWorkspaces();
    } catch (error) {
      toast({ title: 'Failed', description: error.response?.data?.detail || 'Could not create workspace', variant: 'destructive' });
    }
  };

  const handleSubmitTicket = async () => {
    if (!ticketForm.subject.trim() || !ticketForm.message.trim()) return;
    try {
      await supportAPI.createTicket(ticketForm.subject, ticketForm.message, ticketForm.priority);
      toast({ title: 'Ticket Created!', description: 'Our team will respond soon.' });
      setShowSupportModal(false);
      setTicketForm({ subject: '', message: '', priority: 'medium' });
      fetchTickets();
    } catch {
      toast({ title: 'Failed', description: 'Could not create ticket.', variant: 'destructive' });
    }
  };

  const toggleDataSource = (name) => {
    setNewWorkspace(prev => ({
      ...prev,
      dataSources: prev.dataSources.includes(name)
        ? prev.dataSources.filter(n => n !== name)
        : [...prev.dataSources, name]
    }));
  };

  const fetchSlackStatus = async () => {
    try {
      const res = await api.get('/slack/status');
      if (res.data.connected) {
        setSlackConnected(true);
        setSlackTeam(res.data.team_name || '');
        fetchSlackChannels();
      }
    } catch { /* not connected */ }
  };

  const fetchSlackChannels = async () => {
    try {
      const res = await api.get('/slack/channels');
      setSlackChannels(res.data.channels || []);
    } catch { /* ignore */ }
  };

  const handleConnectSlack = async () => {
    if (!slackToken.trim()) return;
    setIsConnectingSlack(true);
    try {
      const res = await api.post('/slack/connect', { bot_token: slackToken });
      setSlackConnected(true);
      setSlackTeam(res.data.team_name || '');
      setSlackToken('');
      fetchSlackChannels();
      toast({ title: 'Slack Connected!', description: res.data.message });
    } catch (error) {
      toast({ title: 'Connection Failed', description: error.response?.data?.detail || 'Invalid token', variant: 'destructive' });
    } finally { setIsConnectingSlack(false); }
  };

  const handleDisconnectSlack = async () => {
    try {
      await api.delete('/slack/disconnect');
      setSlackConnected(false);
      setSlackTeam('');
      setSlackChannels([]);
      toast({ title: 'Disconnected', description: 'Slack workspace disconnected.' });
    } catch { toast({ title: 'Error', description: 'Failed to disconnect.', variant: 'destructive' }); }
  };

  const handleSendToSlack = async () => {
    if (!selectedChannel || !slackMessage.trim()) return;
    try {
      await api.post('/slack/send', { channel_id: selectedChannel, message: slackMessage });
      toast({ title: 'Sent!', description: 'Report shared to Slack channel.' });
      setSlackMessage('');
    } catch (error) {
      toast({ title: 'Failed', description: error.response?.data?.detail || 'Could not send.', variant: 'destructive' });
    }
  };

  const handleAnalyzeUrl = async () => {
    if (!aiUrl.trim()) return;
    setIsAnalyzing(true);
    setAiAnalysis(null);
    try {
      const response = await api.post('/ai-visibility/analyze', { url: aiUrl });
      setAiAnalysis(response.data.analysis);
      toast({ title: 'Analysis Complete!', description: `Analyzed ${aiUrl}` });
    } catch (error) {
      const detail = error.response?.data?.detail || '';
      if (detail.includes('AI_VISIBILITY_LIMIT_REACHED')) {
        setShowUpgradeModal(true);
        toast({ title: 'Monthly Limit Reached', description: 'Starter plan allows 1 AI Visibility analysis per month. Upgrade to Business Pro for unlimited.', variant: 'destructive' });
      } else {
        toast({ title: 'Analysis Failed', description: detail || 'Could not analyze URL', variant: 'destructive' });
      }
    } finally { setIsAnalyzing(false); }
  };

  const handleUpgrade = async (planName) => {
    setIsProcessingPayment(true);
    try {
      const response = await api.post('/payments/create-order', { plan: planName, return_url: window.location.origin });
      const { payment_session_id, order_id } = response.data;
      
      // Load Cashfree SDK
      const script = document.createElement('script');
      script.src = 'https://sdk.cashfree.com/js/core/3.0.0/cashfree.pro.min.js';
      script.async = true;
      document.body.appendChild(script);
      script.onload = async () => {
        try {
          const cashfree = window.Cashfree({ mode: 'production' });
          await cashfree.checkout({ paymentSessionId: payment_session_id, returnUrl: `${window.location.origin}/dashboard?payment_status=success&order_id=${order_id}` });
        } catch (err) {
          toast({ title: 'Payment Failed', description: 'Checkout could not be loaded.', variant: 'destructive' });
        }
      };
    } catch (error) {
      toast({ title: 'Payment Error', description: error.response?.data?.detail || 'Failed to create payment order.', variant: 'destructive' });
    } finally { setIsProcessingPayment(false); }
  };

  // Check payment status on return
  useEffect(() => {
    const paymentStatus = searchParams.get('payment_status');
    const orderId = searchParams.get('order_id');
    if (paymentStatus === 'success' && orderId) {
      api.get(`/payments/order-status/${orderId}`).then(res => {
        if (res.data.order_status === 'PAID') {
          toast({ title: 'Payment Successful!', description: 'Your plan has been upgraded.' });
          refreshUser();
        }
      }).catch(() => {});
    }
  }, [searchParams, refreshUser]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  if (!user) return <div className="min-h-screen bg-gray-950 flex items-center justify-center"><div className="text-gray-400">Loading...</div></div>;

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Slack Floating Panel - Right Side */}
      <div className="fixed top-20 right-4 z-30" data-testid="slack-panel">
        {showSlackPanel ? (
          <Card className="bg-gray-900 border-gray-700 w-80 shadow-2xl shadow-black/50">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-white text-base flex items-center">
                  <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="none"><path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zm1.271 0a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313zM8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zm0 1.271a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312zM18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zm-1.27 0a2.528 2.528 0 0 1-2.523 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.163 0a2.528 2.528 0 0 1 2.523 2.522v6.312zM15.163 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.163 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52zm0-1.27a2.527 2.527 0 0 1-2.52-2.523 2.526 2.526 0 0 1 2.52-2.52h6.315A2.528 2.528 0 0 1 24 15.163a2.528 2.528 0 0 1-2.522 2.523h-6.315z" fill="#E01E5A"/></svg>
                  Slack
                </CardTitle>
                <Button variant="ghost" size="sm" className="text-gray-400 h-6 w-6 p-0" onClick={() => setShowSlackPanel(false)}><X className="w-4 h-4" /></Button>
              </div>
            </CardHeader>
            <CardContent className="pt-0 space-y-3">
              {slackConnected ? (
                <>
                  <div className="flex items-center justify-between bg-green-900/20 border border-green-700/30 rounded-lg p-2.5">
                    <div className="flex items-center space-x-2"><CheckCircle className="w-4 h-4 text-green-400" /><span className="text-green-300 text-sm">{slackTeam}</span></div>
                    <Button variant="ghost" size="sm" className="text-red-400 text-xs h-6 px-2" onClick={handleDisconnectSlack}>Disconnect</Button>
                  </div>
                  <div className="space-y-2">
                    <Label className="text-gray-400 text-xs">Channel</Label>
                    <select value={selectedChannel} onChange={(e) => setSelectedChannel(e.target.value)} className="w-full rounded-md bg-gray-800 border border-gray-700 text-white text-sm px-2.5 py-2 focus:outline-none focus:ring-1 focus:ring-purple-500" data-testid="slack-channel-select">
                      <option value="">Select channel</option>
                      {slackChannels.map(ch => <option key={ch.id} value={ch.id}><Hash className="w-3 h-3" /> #{ch.name}</option>)}
                    </select>
                  </div>
                  <div className="space-y-2">
                    <Label className="text-gray-400 text-xs">Message</Label>
                    <textarea value={slackMessage} onChange={(e) => setSlackMessage(e.target.value)} rows={3} placeholder="Share analytics insights with your team..." className="w-full rounded-md bg-gray-800 border border-gray-700 text-white placeholder:text-gray-500 px-2.5 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-purple-500" data-testid="slack-message-input" />
                  </div>
                  <Button className="w-full bg-[#4A154B] hover:bg-[#3a1039] text-white text-sm" onClick={handleSendToSlack} disabled={!selectedChannel || !slackMessage.trim()} data-testid="slack-send-button">
                    <Send className="w-3.5 h-3.5 mr-2" /> Share to Slack
                  </Button>
                </>
              ) : (
                <div className="space-y-3">
                  <p className="text-gray-400 text-xs">Connect your Slack workspace to share reports with your team.</p>
                  <div className="space-y-2">
                    <Label className="text-gray-400 text-xs">Bot Token (xoxb-...)</Label>
                    <Input value={slackToken} onChange={(e) => setSlackToken(e.target.value)} placeholder="xoxb-your-bot-token" className="bg-gray-800 border-gray-700 text-white text-sm" type="password" data-testid="slack-token-input" />
                  </div>
                  <p className="text-gray-500 text-[10px]">Create a Slack App at <a href="https://api.slack.com/apps" target="_blank" rel="noopener noreferrer" className="text-purple-400 hover:text-purple-300">api.slack.com/apps</a> and copy the Bot Token.</p>
                  <Button className="w-full bg-[#4A154B] hover:bg-[#3a1039] text-white text-sm" onClick={handleConnectSlack} disabled={isConnectingSlack || !slackToken.trim()} data-testid="slack-connect-button">
                    {isConnectingSlack ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Connect Slack'}
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        ) : (
          <Button onClick={() => setShowSlackPanel(true)} className="bg-[#4A154B] hover:bg-[#3a1039] text-white shadow-lg shadow-black/30 rounded-full px-4 py-2" data-testid="slack-open-button">
            <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="none"><path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zm1.271 0a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313zM8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zm0 1.271a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312zM18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zm-1.27 0a2.528 2.528 0 0 1-2.523 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.163 0a2.528 2.528 0 0 1 2.523 2.522v6.312zM15.163 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.163 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52zm0-1.27a2.527 2.527 0 0 1-2.52-2.523 2.526 2.526 0 0 1 2.52-2.52h6.315A2.528 2.528 0 0 1 24 15.163a2.528 2.528 0 0 1-2.522 2.523h-6.315z" fill="currentColor"/></svg>
            Slack
          </Button>
        )}
      </div>

      {/* Trial Expired Overlay */}
      {trialExpired && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center">
          <Card className="bg-gray-900 border-gray-700 max-w-md mx-4">
            <CardContent className="p-8 text-center">
              <AlertTriangle className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-white mb-2">Trial Period Ended</h2>
              <p className="text-gray-400 mb-6">Your 14-day free trial has expired. Upgrade to continue using Analiyx.</p>
              <Button className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white" data-testid="upgrade-button" onClick={() => { setTrialExpired(false); setShowUpgradeModal(true); }}>
                Upgrade Now
              </Button>
              <Button variant="ghost" className="w-full mt-2 text-gray-400" onClick={handleLogout}>Logout</Button>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Floating Trial Badge */}
      {trialDaysLeft !== null && trialDaysLeft > 0 && (
        <div className="fixed bottom-6 left-6 z-40" data-testid="trial-badge">
          <div className={`flex items-center space-x-2 px-4 py-2.5 rounded-full shadow-lg border ${trialDaysLeft <= 3 ? 'bg-red-900/90 border-red-700 text-red-200' : 'bg-gray-900/90 border-purple-700 text-purple-200'} backdrop-blur-sm`}>
            <Clock className="w-4 h-4" />
            <span className="text-sm font-medium">{trialDaysLeft} day{trialDaysLeft !== 1 ? 's' : ''} left in trial</span>
          </div>
        </div>
      )}

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
            <div className="flex items-center space-x-3">
              <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white" onClick={() => setShowSupportModal(true)} data-testid="support-button">
                <MessageSquare className="w-4 h-4 mr-1" /> Support
              </Button>
              <Button variant="ghost" className="text-gray-400 hover:text-white" onClick={handleLogout} data-testid="logout-button">
                <LogOut className="w-5 h-5 mr-2" /> Logout
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Welcome, {user.name}!</h1>
            <p className="text-gray-400">Manage your data analytics and subscriptions</p>
          </div>
          <Button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white" onClick={() => setShowWorkspaceModal(true)} data-testid="new-workspace-button">
            <Plus className="w-4 h-4 mr-2" /> New Workspace
          </Button>
        </div>

        {/* User Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-gray-900 border-gray-800"><CardContent className="p-6"><div className="flex items-center space-x-4"><div className="p-3 bg-purple-900/20 rounded-lg"><CreditCard className="w-6 h-6 text-purple-400" /></div><div><p className="text-gray-400 text-sm">Current Plan</p><p className="text-xl font-bold text-white">{user.plan}</p></div></div></CardContent></Card>
          <Card className="bg-gray-900 border-gray-800"><CardContent className="p-6"><div className="flex items-center space-x-4"><div className="p-3 bg-green-900/20 rounded-lg"><TrendingUp className="w-6 h-6 text-green-400" /></div><div><p className="text-gray-400 text-sm">Credits Available</p><p className="text-xl font-bold text-white">{user.credits}</p></div></div></CardContent></Card>
          <Card className="bg-gray-900 border-gray-800"><CardContent className="p-6"><div className="flex items-center space-x-4"><div className="p-3 bg-blue-900/20 rounded-lg"><Database className="w-6 h-6 text-blue-400" /></div><div><p className="text-gray-400 text-sm">Account Status</p><p className="text-xl font-bold text-white capitalize">{user.status}</p></div></div></CardContent></Card>
        </div>

        {/* Workspaces */}
        {workspaces.length > 0 && (
          <Card className="bg-gray-900 border-gray-800 mb-6">
            <CardHeader><CardTitle className="text-white flex items-center"><Folder className="w-5 h-5 mr-2" /> Your Workspaces</CardTitle></CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {workspaces.map((ws) => (
                  <div key={ws.id} className="bg-gray-800/50 rounded-lg p-4 border border-gray-700 hover:border-purple-500/50 transition-colors">
                    <h3 className="text-white font-medium mb-1">{ws.name}</h3>
                    <p className="text-gray-400 text-xs mb-2">{ws.data_sources.length} data source{ws.data_sources.length !== 1 ? 's' : ''}</p>
                    <div className="flex flex-wrap gap-1">{ws.data_sources.map((ds, i) => <span key={i} className="text-xs bg-gray-700 text-gray-300 px-2 py-0.5 rounded">{ds}</span>)}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Uploaded Files with Graphical Analytics */}
        {uploadedFiles.length > 0 && (
          <Card className="bg-gray-900 border-gray-800 mb-6">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-white flex items-center"><FileSpreadsheet className="w-5 h-5 mr-2" /> Your Uploaded Files</CardTitle>
                <Button variant="outline" size="sm" onClick={handleDownloadReport} className="border-purple-500 text-purple-400 hover:bg-purple-900/20" data-testid="download-reports-button"><Download className="w-4 h-4 mr-2" /> Download All Reports</Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {uploadedFiles.map((file) => (
                  <div key={file.id} className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition-colors cursor-pointer" onClick={() => handleViewFileDetails(file.id)}>
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 bg-green-900/20 rounded-lg flex items-center justify-center"><CheckCircle className="w-5 h-5 text-green-500" /></div>
                      <div>
                        <p className="text-white font-medium">{file.filename}</p>
                        <p className="text-gray-400 text-sm">{file.total_rows} rows x {file.total_columns} columns</p>
                      </div>
                    </div>
                    <Button variant="ghost" size="sm" className="text-purple-400 hover:text-purple-300">View Analytics</Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Connect More Sources CTA */}
        <Card className="bg-gradient-to-br from-purple-900/20 to-pink-900/20 border-purple-500/30 mt-6">
          <CardContent className="p-8 text-center">
            <Sparkles className="w-12 h-12 text-purple-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">Connect More Data Sources</h3>
            <p className="text-gray-400 mb-6">Get deeper insights by connecting all your business data sources</p>
            <div className="flex justify-center space-x-3">
              <Button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white" onClick={() => setIsDataSourceModalOpen(true)} data-testid="browse-integrations-button">Browse Integrations</Button>
              <Button variant="outline" className="border-gray-700 text-gray-300 hover:bg-gray-800" onClick={() => window.location.href = 'mailto:techmeliora@gmail.com'}>
                <Mail className="w-4 h-4 mr-2" /> Contact Support
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* AI Visibility Section */}
        <Card className="bg-gray-900 border-gray-800 mt-6">
          <CardHeader>
            <CardTitle className="text-white flex items-center"><Globe className="w-5 h-5 mr-2 text-purple-400" /> AI Visibility Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-400 text-sm mb-4">Enter any URL to analyze its SEO performance, content quality, and AI discoverability</p>
            <div className="flex space-x-3">
              <Input value={aiUrl} onChange={(e) => setAiUrl(e.target.value)} placeholder="https://example.com" className="bg-gray-800 border-gray-700 text-white flex-1" data-testid="ai-url-input" />
              <Button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700" onClick={handleAnalyzeUrl} disabled={isAnalyzing || !aiUrl.trim()} data-testid="analyze-url-button">
                {isAnalyzing ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Analyzing...</> : <><Search className="w-4 h-4 mr-2" />Analyze</>}
              </Button>
            </div>

            {/* AI Analysis Results */}
            {aiAnalysis && (
              <div className="mt-6 space-y-4" data-testid="ai-analysis-results">
                {/* Score Cards */}
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                  {[
                    { label: 'Overall', value: aiAnalysis.overall_score, color: 'text-purple-400' },
                    { label: 'SEO', value: aiAnalysis.seo_score, color: 'text-blue-400' },
                    { label: 'AI Visibility', value: aiAnalysis.ai_visibility_score, color: 'text-green-400' },
                    { label: 'Content', value: aiAnalysis.content_quality_score, color: 'text-yellow-400' },
                    { label: 'Technical', value: aiAnalysis.technical_seo_score, color: 'text-pink-400' },
                  ].map((score, i) => (
                    <div key={i} className="bg-gray-800 rounded-lg p-3 text-center">
                      <p className="text-gray-500 text-xs mb-1">{score.label}</p>
                      <p className={`text-2xl font-bold ${score.color}`}>{score.value}<span className="text-xs text-gray-500">/100</span></p>
                      <div className="w-full bg-gray-700 rounded-full h-1.5 mt-2"><div className={`h-1.5 rounded-full ${score.value >= 70 ? 'bg-green-500' : score.value >= 40 ? 'bg-yellow-500' : 'bg-red-500'}`} style={{ width: `${score.value}%` }}></div></div>
                    </div>
                  ))}
                </div>

                {/* Summary */}
                <div className="bg-gray-800/50 rounded-lg p-4"><p className="text-gray-300 text-sm">{aiAnalysis.summary}</p></div>

                {/* Strengths & Improvements */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <h4 className="text-green-400 font-medium mb-3 flex items-center"><CheckCircle className="w-4 h-4 mr-2" /> Strengths</h4>
                    <ul className="space-y-2">{(aiAnalysis.strengths || []).map((s, i) => <li key={i} className="text-gray-300 text-sm flex items-start"><span className="text-green-500 mr-2">+</span>{s}</li>)}</ul>
                  </div>
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <h4 className="text-yellow-400 font-medium mb-3 flex items-center"><AlertTriangle className="w-4 h-4 mr-2" /> Improvements</h4>
                    <ul className="space-y-2">{(aiAnalysis.improvements || []).map((s, i) => <li key={i} className="text-gray-300 text-sm flex items-start"><span className="text-yellow-500 mr-2">-</span>{s}</li>)}</ul>
                  </div>
                </div>

                {/* AI Recommendations */}
                {aiAnalysis.ai_recommendations?.length > 0 && (
                  <div className="bg-purple-900/20 border border-purple-700/30 rounded-lg p-4">
                    <h4 className="text-purple-400 font-medium mb-3 flex items-center"><Brain className="w-4 h-4 mr-2" /> AI Discoverability Tips</h4>
                    <ul className="space-y-2">{aiAnalysis.ai_recommendations.map((r, i) => <li key={i} className="text-gray-300 text-sm flex items-start"><Zap className="w-3 h-3 text-purple-400 mr-2 mt-0.5 flex-shrink-0" />{r}</li>)}</ul>
                  </div>
                )}

                {/* Keywords */}
                {aiAnalysis.keyword_suggestions?.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    <span className="text-gray-500 text-sm">Suggested Keywords:</span>
                    {aiAnalysis.keyword_suggestions.map((kw, i) => <span key={i} className="text-xs bg-gray-800 text-purple-300 px-3 py-1 rounded-full border border-purple-700/30">{kw}</span>)}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </main>

      {/* Data Source Modal */}
      <Dialog open={isDataSourceModalOpen} onOpenChange={setIsDataSourceModalOpen}>
        <DialogContent className="bg-gray-900 border-gray-800 text-white max-w-3xl">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold">{showFileUpload ? 'Upload File' : 'Connect Data Source'}</DialogTitle>
            <DialogDescription className="text-gray-400">{showFileUpload ? 'Upload your CSV or Excel file' : 'Choose a data source to connect'}</DialogDescription>
          </DialogHeader>
          {showFileUpload ? (
            <div className="py-6">
              <div className="border-2 border-dashed border-gray-700 rounded-xl p-8 text-center hover:border-purple-500 transition-colors">
                <input type="file" accept=".csv,.xlsx,.xls" onChange={handleFileSelect} className="hidden" id="file-upload" />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-white font-semibold mb-2">{selectedFile ? selectedFile.name : 'Click to upload'}</p>
                  <p className="text-gray-400 text-sm">CSV or Excel files (max 10MB)</p>
                </label>
              </div>
              {selectedFile && (
                <div className="mt-4 bg-gray-800 rounded-lg p-4 flex items-center justify-between">
                  <div className="flex items-center space-x-3"><FileSpreadsheet className="w-8 h-8 text-green-500" /><div><p className="text-white font-medium">{selectedFile.name}</p><p className="text-gray-400 text-sm">{(selectedFile.size / 1024).toFixed(2)} KB</p></div></div>
                  <Button variant="ghost" size="sm" onClick={() => setSelectedFile(null)} className="text-gray-400"><X className="w-4 h-4" /></Button>
                </div>
              )}
              <div className="flex space-x-3 mt-6">
                <Button variant="outline" className="flex-1 border-gray-700 text-gray-300" onClick={() => { setShowFileUpload(false); setSelectedFile(null); }}>Back</Button>
                <Button className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600" onClick={handleFileUpload} disabled={!selectedFile || isUploading}>
                  {isUploading ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Uploading...</> : <><Upload className="w-4 h-4 mr-2" />Upload & Analyze</>}
                </Button>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 py-4">
              {integrations.map((integration, index) => (
                <button key={index} className="group bg-gray-800 border border-gray-700 rounded-xl p-4 hover:border-purple-500 transition-all duration-300 transform hover:scale-105" onClick={() => handleIntegrationClick(integration)}>
                  <div className="flex flex-col items-center space-y-2">
                    <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${integration.color}20` }}>
                      <Database className="w-6 h-6" style={{ color: integration.color }} />
                    </div>
                    <span className="text-xs text-gray-400 text-center group-hover:text-white">{integration.name}</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* File Analytics Modal - GRAPHICAL */}
      <Dialog open={showFileDetails} onOpenChange={setShowFileDetails}>
        <DialogContent className="bg-gray-900 border-gray-800 text-white max-w-5xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold">File Analytics</DialogTitle>
            <DialogDescription className="text-gray-400">{fileDetails?.filename}</DialogDescription>
          </DialogHeader>
          {fileDetails && (
            <div className="space-y-6 py-4">
              {/* Summary Cards */}
              <div className="grid grid-cols-3 gap-4">
                <Card className="bg-gray-800 border-gray-700"><CardContent className="p-4 text-center"><p className="text-gray-400 text-sm">Rows</p><p className="text-3xl font-bold text-purple-400">{fileDetails.analytics.total_rows.toLocaleString()}</p></CardContent></Card>
                <Card className="bg-gray-800 border-gray-700"><CardContent className="p-4 text-center"><p className="text-gray-400 text-sm">Columns</p><p className="text-3xl font-bold text-blue-400">{fileDetails.analytics.total_columns}</p></CardContent></Card>
                <Card className="bg-gray-800 border-gray-700"><CardContent className="p-4 text-center"><p className="text-gray-400 text-sm">Type</p><p className="text-3xl font-bold text-green-400">{fileDetails.source_type}</p></CardContent></Card>
              </div>

              {/* Data Types Distribution - Pie-like Visual */}
              <Card className="bg-gray-800 border-gray-700">
                <CardHeader><CardTitle className="text-white text-lg">Column Data Types</CardTitle></CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-3">
                      {Object.entries(
                        fileDetails.analytics.columns.reduce((acc, col) => {
                          const type = fileDetails.analytics.data_types[col] || 'unknown';
                          acc[type] = (acc[type] || 0) + 1;
                          return acc;
                        }, {})
                      ).map(([type, count], i) => {
                        const colors = ['bg-purple-500', 'bg-blue-500', 'bg-green-500', 'bg-yellow-500', 'bg-pink-500', 'bg-cyan-500'];
                        const total = fileDetails.analytics.total_columns;
                        const pct = Math.round((count / total) * 100);
                        return (
                          <div key={type}>
                            <div className="flex justify-between text-sm mb-1">
                              <span className="text-gray-300">{type}</span>
                              <span className="text-gray-400">{count} ({pct}%)</span>
                            </div>
                            <div className="w-full bg-gray-700 rounded-full h-3">
                              <div className={`${colors[i % colors.length]} h-3 rounded-full transition-all duration-500`} style={{ width: `${pct}%` }}></div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                    {/* Missing Values Chart */}
                    <div>
                      <p className="text-sm text-gray-400 mb-3">Missing Values by Column</p>
                      <div className="flex items-end space-x-1 h-40">
                        {fileDetails.analytics.columns.slice(0, 10).map((col, i) => {
                          const missing = fileDetails.analytics.missing_values[col] || 0;
                          const total = fileDetails.analytics.total_rows;
                          const pct = total > 0 ? Math.max((missing / total) * 100, 2) : 2;
                          return (
                            <div key={i} className="flex-1 flex flex-col items-center group" title={`${col}: ${missing} missing`}>
                              <div className={`w-full rounded-t ${missing > 0 ? 'bg-yellow-500' : 'bg-green-500'} transition-all`} style={{ height: `${Math.min(pct, 100)}%`, minHeight: '8px' }}></div>
                              <span className="text-[9px] text-gray-500 mt-1 truncate w-full text-center">{col.slice(0, 6)}</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Numeric Summary - Bar Chart */}
              {fileDetails.analytics.numeric_summary && Object.keys(fileDetails.analytics.numeric_summary).length > 0 && (
                <Card className="bg-gray-800 border-gray-700">
                  <CardHeader><CardTitle className="text-white text-lg">Numeric Column Statistics</CardTitle></CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {Object.entries(fileDetails.analytics.numeric_summary).map(([col, stats]) => {
                        const min = stats.min || 0;
                        const max = stats.max || 1;
                        const mean = stats.mean || 0;
                        const range = max - min || 1;
                        const meanPct = ((mean - min) / range) * 100;
                        return (
                          <div key={col} className="bg-gray-700/50 rounded-lg p-4">
                            <div className="flex justify-between mb-2">
                              <span className="text-white font-medium">{col}</span>
                              <span className="text-gray-400 text-sm">Mean: {typeof mean === 'number' ? mean.toFixed(2) : 'N/A'}</span>
                            </div>
                            <div className="relative w-full bg-gray-600 rounded-full h-4">
                              <div className="absolute left-0 top-0 h-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full" style={{ width: `${Math.min(meanPct, 100)}%` }}></div>
                              <div className="absolute top-0 h-4 w-0.5 bg-white" style={{ left: `${Math.min(meanPct, 100)}%` }}></div>
                            </div>
                            <div className="flex justify-between text-xs text-gray-500 mt-1">
                              <span>Min: {typeof min === 'number' ? min.toFixed(2) : min}</span>
                              <span>Max: {typeof max === 'number' ? max.toFixed(2) : max}</span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Sample Data Table */}
              {fileDetails.sample_data?.length > 0 && (
                <Card className="bg-gray-800 border-gray-700">
                  <CardHeader><CardTitle className="text-white text-lg">Sample Data (First 5 Rows)</CardTitle></CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead><tr className="border-b border-gray-700">{Object.keys(fileDetails.sample_data[0]).map((key, idx) => <th key={idx} className="text-left py-2 px-3 text-gray-400 font-medium">{key}</th>)}</tr></thead>
                        <tbody>{fileDetails.sample_data.map((row, idx) => <tr key={idx} className="border-b border-gray-700">{Object.values(row).map((v, vi) => <td key={vi} className="py-2 px-3 text-gray-300">{String(v)}</td>)}</tr>)}</tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              )}

              <div className="flex space-x-3">
                <Button className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600" onClick={() => downloadComprehensiveReport({ files: uploadedFiles, fileDetails }, 'excel')}><Download className="w-4 h-4 mr-2" /> Download Report</Button>
                <Button variant="outline" className="border-gray-700 text-gray-300" onClick={() => setShowFileDetails(false)}>Close</Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Workspace Creation Modal */}
      <Dialog open={showWorkspaceModal} onOpenChange={setShowWorkspaceModal}>
        <DialogContent className="bg-gray-900 border-gray-800 text-white max-w-lg">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold">Create New Workspace</DialogTitle>
            <DialogDescription className="text-gray-400">Set up a workspace and select data sources</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label className="text-gray-300">Workspace Name</Label>
              <Input value={newWorkspace.name} onChange={(e) => setNewWorkspace(p => ({...p, name: e.target.value}))} placeholder="e.g., Marketing Analytics" className="bg-gray-800 border-gray-700 text-white" data-testid="workspace-name-input" />
            </div>
            <div className="space-y-2">
              <Label className="text-gray-300">Select Data Sources</Label>
              <div className="grid grid-cols-3 gap-2">
                {['Excel', 'CSV', 'Google Ads', 'Meta Ads', 'Google Sheets', 'Zoho Books', 'Google Analytics', 'Shopify'].map(ds => (
                  <button key={ds} onClick={() => toggleDataSource(ds)} className={`px-3 py-2 rounded-lg text-xs border transition-all ${newWorkspace.dataSources.includes(ds) ? 'bg-purple-900/40 border-purple-500 text-purple-300' : 'bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-600'}`}>
                    {ds}
                  </button>
                ))}
              </div>
            </div>
            <Button className="w-full bg-gradient-to-r from-purple-600 to-pink-600" onClick={handleCreateWorkspace} disabled={!newWorkspace.name.trim()} data-testid="create-workspace-button">
              <Plus className="w-4 h-4 mr-2" /> Create Workspace
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Support Ticket Modal */}
      <Dialog open={showSupportModal} onOpenChange={setShowSupportModal}>
        <DialogContent className="bg-gray-900 border-gray-800 text-white max-w-lg">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold">Contact Support</DialogTitle>
            <DialogDescription className="text-gray-400">Raise a ticket or email us at techmeliora@gmail.com</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label className="text-gray-300">Subject</Label>
              <Input value={ticketForm.subject} onChange={(e) => setTicketForm(p => ({...p, subject: e.target.value}))} placeholder="Brief description of your issue" className="bg-gray-800 border-gray-700 text-white" data-testid="ticket-subject-input" />
            </div>
            <div className="space-y-2">
              <Label className="text-gray-300">Priority</Label>
              <div className="flex space-x-2">
                {['low', 'medium', 'high'].map(p => (
                  <button key={p} onClick={() => setTicketForm(prev => ({...prev, priority: p}))} className={`px-4 py-2 rounded-lg text-sm capitalize ${ticketForm.priority === p ? 'bg-purple-900/40 border-purple-500 text-purple-300 border' : 'bg-gray-800 border border-gray-700 text-gray-400'}`}>{p}</button>
                ))}
              </div>
            </div>
            <div className="space-y-2">
              <Label className="text-gray-300">Message</Label>
              <textarea value={ticketForm.message} onChange={(e) => setTicketForm(p => ({...p, message: e.target.value}))} rows={4} placeholder="Describe your issue in detail..." className="w-full rounded-md bg-gray-800 border border-gray-700 text-white placeholder:text-gray-500 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500" data-testid="ticket-message-input" />
            </div>
            <div className="flex space-x-3">
              <Button className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600" onClick={handleSubmitTicket} data-testid="submit-ticket-button"><Send className="w-4 h-4 mr-2" /> Submit Ticket</Button>
              <Button variant="outline" className="border-gray-700 text-gray-300" onClick={() => window.location.href = 'mailto:techmeliora@gmail.com'}><Mail className="w-4 h-4 mr-2" /> Email Us</Button>
            </div>

            {/* Previous Tickets */}
            {tickets.length > 0 && (
              <div className="mt-4 border-t border-gray-800 pt-4">
                <p className="text-sm text-gray-400 mb-3">Your Previous Tickets</p>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {tickets.map(t => (
                    <div key={t.id} className="bg-gray-800 rounded-lg p-3 flex justify-between items-center">
                      <div>
                        <p className="text-white text-sm">{t.subject}</p>
                        <p className="text-gray-500 text-xs">{new Date(t.created_at).toLocaleDateString()}</p>
                      </div>
                      <span className={`text-xs px-2 py-1 rounded-full ${t.status === 'open' ? 'bg-yellow-900/30 text-yellow-400' : 'bg-green-900/30 text-green-400'}`}>{t.status}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Upgrade/Payment Modal */}
      <Dialog open={showUpgradeModal} onOpenChange={setShowUpgradeModal}>
        <DialogContent className="bg-gray-900 border-gray-800 text-white max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold">Upgrade Your Plan</DialogTitle>
            <DialogDescription className="text-gray-400">Choose a plan to unlock full Analiyx features</DialogDescription>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-4 py-4">
            {[
              { name: 'Starter', price: '500', credits: '100', features: ['4 Data Sources', 'AI Visibility (1/month)', '1 Workspace'] },
              { name: 'Business Pro', price: '800', credits: '1,000', features: ['Unlimited Sources', 'Unlimited AI Visibility', '10 Workspaces', 'Slack Integration'] }
            ].map((plan) => (
              <div key={plan.name} className={`bg-gray-800 rounded-xl p-6 border ${plan.name === 'Business Pro' ? 'border-purple-500' : 'border-gray-700'}`}>
                <h3 className="text-lg font-bold text-white mb-1">{plan.name}</h3>
                <p className="text-3xl font-bold text-white mb-1">₹{plan.price}<span className="text-sm text-gray-400">/mo</span></p>
                <p className="text-sm text-gray-400 mb-4">{plan.credits} credits/month</p>
                <ul className="space-y-2 mb-6">
                  {plan.features.map((f, i) => <li key={i} className="text-gray-300 text-sm flex items-center"><CheckCircle className="w-3 h-3 text-purple-400 mr-2" />{f}</li>)}
                </ul>
                <Button className="w-full bg-gradient-to-r from-purple-600 to-pink-600" onClick={() => handleUpgrade(plan.name)} disabled={isProcessingPayment || user?.plan === plan.name} data-testid={`upgrade-${plan.name.toLowerCase().replace(' ','-')}`}>
                  {isProcessingPayment ? <Loader2 className="w-4 h-4 animate-spin" /> : user?.plan === plan.name ? 'Current Plan' : 'Upgrade'}
                </Button>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-500 text-center">For Enterprise plans, <a href="mailto:techmeliora@gmail.com" className="text-purple-400 hover:text-purple-300">contact us</a></p>
        </DialogContent>
      </Dialog>

    </div>
  );
};

export default UserDashboard;
