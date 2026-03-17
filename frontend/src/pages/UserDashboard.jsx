import React, { useEffect, useState, useCallback, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Sparkles, LogOut, Database, CreditCard, TrendingUp, X, ArrowUp, ArrowDown, Minus, Brain, Facebook, Megaphone, BarChart, BookOpen, Upload, FileSpreadsheet, CheckCircle, Loader2, Download, Clock, AlertTriangle, Plus, Folder, MessageSquare, Send, Mail, Globe, Search, Zap, Hash, Trash2, Activity, Layers, Eye, ChevronRight, StickyNote, FileBarChart, LayoutDashboard, Pencil, Save } from 'lucide-react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { integrations } from '../mock/mockData';
import { dataSourceAPI, workspaceAPI, supportAPI, authAPI } from '../services/api';
import { toast } from '../hooks/use-toast';
import { downloadComprehensiveReport, exportFilesToExcel } from '../utils/reportExport';
import api from '../services/api';
import Joyride from 'react-joyride';
import WorkspaceView from './WorkspaceView';
import AnalyticsDashboard from '../components/AnalyticsDashboard';

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
  const [aiSearchQuery, setAiSearchQuery] = useState('');
  const [aiSearchResult, setAiSearchResult] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [showTour, setShowTour] = useState(false);
  const [selectedWorkspace, setSelectedWorkspace] = useState(null);
  const [dashboardSummary, setDashboardSummary] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [chartsData, setChartsData] = useState({});
  const [notes, setNotes] = useState([]);
  const [reports, setReports] = useState([]);
  const [showNoteModal, setShowNoteModal] = useState(false);
  const [editingNote, setEditingNote] = useState(null);
  const [noteTitle, setNoteTitle] = useState('');
  const [noteContent, setNoteContent] = useState('');
  const [aiChatInput, setAiChatInput] = useState('');
  const [aiChatMessages, setAiChatMessages] = useState([]);
  const [isChatSending, setIsChatSending] = useState(false);
  const [chatSessionId, setChatSessionId] = useState(null);
  const chatEndRef = useRef(null);

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
    fetchDashboardSummary();
  }, [navigate, refreshUser]);

  const fetchDashboardSummary = async () => {
    try {
      const res = await api.get('/dashboard/summary');
      setDashboardSummary(res.data);
    } catch { }
  };

  const fetchNotes = async () => {
    try {
      const res = await api.get('/charts/notes');
      setNotes(res.data.notes || []);
    } catch { }
  };

  const fetchReports = async () => {
    try {
      const res = await api.get('/charts/reports');
      setReports(res.data.reports || []);
    } catch { }
  };

  const fetchChartsForFile = async (fileId) => {
    if (chartsData[fileId]) return;
    try {
      const res = await api.get(`/charts/generate/${fileId}`);
      setChartsData(prev => ({ ...prev, [fileId]: res.data }));
    } catch { }
  };

  // Auto-generate charts for all uploaded files
  useEffect(() => {
    uploadedFiles.forEach(f => fetchChartsForFile(f.id));
  }, [uploadedFiles]);

  useEffect(() => {
    if (activeTab === 'notes') fetchNotes();
    if (activeTab === 'reports') fetchReports();
  }, [activeTab]);

  // AI Chat on dashboard
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [aiChatMessages]);

  const handleDashboardChat = async () => {
    if (!aiChatInput.trim() || isChatSending) return;
    const msg = aiChatInput.trim();
    setAiChatInput('');
    setAiChatMessages(prev => [...prev, { role: 'user', content: msg }]);
    setIsChatSending(true);
    try {
      const res = await api.post('/ai/chat', { query: msg, session_id: chatSessionId });
      if (res.data.session_id) setChatSessionId(res.data.session_id);
      setAiChatMessages(prev => [...prev, { role: 'assistant', content: res.data.answer, sources: res.data.sources }]);
    } catch {
      setAiChatMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, something went wrong. Please try again.', isError: true }]);
    } finally { setIsChatSending(false); }
  };

  const handleSaveNote = async () => {
    if (!noteTitle.trim()) return;
    try {
      if (editingNote) {
        await api.put(`/charts/notes/${editingNote}`, { title: noteTitle, content: noteContent });
        toast({ title: 'Note Updated' });
      } else {
        await api.post('/charts/notes', { title: noteTitle, content: noteContent });
        toast({ title: 'Note Created' });
      }
      setShowNoteModal(false);
      setEditingNote(null);
      setNoteTitle('');
      setNoteContent('');
      fetchNotes();
    } catch { toast({ title: 'Error', description: 'Failed to save note', variant: 'destructive' }); }
  };

  const handleDeleteNote = async (id) => {
    if (!window.confirm('Delete this note?')) return;
    try {
      await api.delete(`/charts/notes/${id}`);
      toast({ title: 'Note Deleted' });
      fetchNotes();
    } catch { toast({ title: 'Error', variant: 'destructive' }); }
  };

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

  const handleDeleteFile = async (fileId, filename) => {
    if (!window.confirm(`Delete "${filename}"?`)) return;
    try {
      await dataSourceAPI.deleteFile(fileId);
      toast({ title: 'File Deleted', description: `${filename} removed.` });
      fetchUploadedFiles();
    } catch {
      toast({ title: 'Delete Failed', description: 'Could not delete file.', variant: 'destructive' });
    }
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
      toast({ title: 'Failed', description: typeof error.response?.data?.detail === 'string' ? error.response.data.detail : 'Could not create workspace', variant: 'destructive' });
    }
  };

  const handleDeleteWorkspace = async (wsId, wsName) => {
    if (!window.confirm(`Delete workspace "${wsName}"? This cannot be undone.`)) return;
    try {
      await workspaceAPI.delete(wsId);
      toast({ title: 'Workspace Deleted', description: `'${wsName}' has been removed.` });
      fetchWorkspaces();
    } catch (error) {
      toast({ title: 'Delete Failed', description: typeof error.response?.data?.detail === 'string' ? error.response.data.detail : 'Could not delete workspace', variant: 'destructive' });
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
      toast({ title: 'Connection Failed', description: typeof error.response?.data?.detail === 'string' ? error.response.data.detail : 'Invalid token', variant: 'destructive' });
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
      toast({ title: 'Failed', description: typeof error.response?.data?.detail === 'string' ? error.response.data.detail : 'Could not send.', variant: 'destructive' });
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

  const loadCashfreeSDK = useCallback(() => {
    return new Promise((resolve, reject) => {
      if (window.Cashfree) { resolve(); return; }
      const existing = document.querySelector('script[src*="sdk.cashfree.com"]');
      if (existing) { existing.onload = () => resolve(); return; }
      const script = document.createElement('script');
      script.src = 'https://sdk.cashfree.com/js/v3/cashfree.js';
      script.async = true;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error('Failed to load Cashfree SDK'));
      document.body.appendChild(script);
    });
  }, []);

  const handleUpgrade = async (planName) => {
    setIsProcessingPayment(true);
    try {
      const response = await api.post('/payments/create-order', { plan: planName, return_url: window.location.origin });
      const { payment_session_id, order_id } = response.data;
      await loadCashfreeSDK();
      const cashfree = window.Cashfree({ mode: 'production' });
      await cashfree.checkout({
        paymentSessionId: payment_session_id,
        returnUrl: `${window.location.origin}/dashboard?payment_status=success&order_id=${order_id}`
      });
    } catch (error) {
      toast({ title: 'Payment Error', description: error.response?.data?.detail || 'Failed to initiate payment. Please try again.', variant: 'destructive' });
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

  const handleAiSearch = async () => {
    if (!aiSearchQuery.trim()) return;
    setIsSearching(true);
    try {
      const res = await api.post('/ai/search', { query: aiSearchQuery });
      setAiSearchResult(res.data);
    } catch (error) {
      toast({ title: 'Search Failed', description: error.response?.data?.detail || 'AI search failed', variant: 'destructive' });
    } finally { setIsSearching(false); }
  };

  // Show tour for first-time users
  useEffect(() => {
    const tourSeen = localStorage.getItem('analiyx_tour_seen');
    if (!tourSeen && user) setShowTour(true);
  }, [user]);

  const handleTourEnd = (data) => {
    if (data.status === 'finished' || data.status === 'skipped') {
      setShowTour(false);
      localStorage.setItem('analiyx_tour_seen', 'true');
    }
  };

  const tourSteps = [
    { target: '[data-testid="new-workspace-button"]', content: 'Create workspaces to organize your data sources and analytics.' },
    { target: '[data-testid="browse-integrations-button"]', content: 'Connect your data sources like Excel, CSV, Google Analytics, and more.' },
    { target: '[data-testid="support-button"]', content: 'Need help? Create a support ticket and our team will assist you.' },
  ];

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  if (!user) return <div className="min-h-screen bg-gray-950 flex items-center justify-center"><div className="text-gray-400">Loading...</div></div>;

  // Workspace Detail View
  if (selectedWorkspace) {
    return <WorkspaceView workspace={selectedWorkspace} onBack={() => setSelectedWorkspace(null)} user={user} />;
  }

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
          <Card className="bg-gray-900 border-gray-700 max-w-2xl mx-4">
            <CardContent className="p-8">
              <div className="text-center mb-6">
                <AlertTriangle className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-white mb-2">Trial Period Ended</h2>
                <p className="text-gray-400">Your 14-day free trial has expired. Select a plan to continue using Analiyx.</p>
              </div>
              <div className="grid grid-cols-2 gap-4 mb-6">
                {[
                  { name: 'Starter', price: '500', features: ['4 Data Sources', 'AI Visibility (1/month)', '100 Credits', '1 Workspace'] },
                  { name: 'Business Pro', price: '800', features: ['Unlimited Sources', 'Unlimited AI Visibility', '1,000 Credits', '10 Workspaces', 'Slack Integration'] }
                ].map((plan) => (
                  <div key={plan.name} className={`bg-gray-800 rounded-xl p-5 border ${plan.name === 'Business Pro' ? 'border-purple-500' : 'border-gray-700'}`}>
                    {plan.name === 'Business Pro' && <span className="text-xs bg-purple-600 text-white px-2 py-0.5 rounded-full">Recommended</span>}
                    <h3 className="text-lg font-bold text-white mt-2">{plan.name}</h3>
                    <p className="text-2xl font-bold text-white mb-3">₹{plan.price}<span className="text-sm text-gray-400">/mo</span></p>
                    <ul className="space-y-1.5 mb-4">
                      {plan.features.map((f, i) => <li key={i} className="text-gray-300 text-sm flex items-center"><CheckCircle className="w-3 h-3 text-purple-400 mr-2 flex-shrink-0" />{f}</li>)}
                    </ul>
                    <Button className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white" onClick={() => handleUpgrade(plan.name)} disabled={isProcessingPayment} data-testid={`trial-upgrade-${plan.name.toLowerCase().replace(' ','-')}`}>
                      {isProcessingPayment ? <Loader2 className="w-4 h-4 animate-spin" /> : `Select ${plan.name}`}
                    </Button>
                  </div>
                ))}
              </div>
              <p className="text-xs text-gray-500 text-center mb-3">For Enterprise plans, <a href="mailto:techmeliora@gmail.com" className="text-purple-400">contact us</a></p>
              <Button variant="ghost" className="w-full text-gray-500 text-sm" onClick={handleLogout}>Logout</Button>
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

      {/* Guided Tour */}
      <Joyride
        steps={tourSteps}
        run={showTour}
        continuous
        showSkipButton
        showProgress
        callback={handleTourEnd}
        styles={{
          options: { primaryColor: '#9333ea', zIndex: 10000, backgroundColor: '#1f2937', textColor: '#e5e7eb', arrowColor: '#1f2937' },
          tooltip: { borderRadius: 12 },
          buttonNext: { backgroundColor: '#9333ea', borderRadius: 8 },
          buttonBack: { color: '#9ca3af' },
          buttonSkip: { color: '#9ca3af' },
        }}
      />

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
              <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white" onClick={() => { localStorage.removeItem('analiyx_tour_seen'); setShowTour(true); }} data-testid="take-tour-button">
                <Sparkles className="w-4 h-4 mr-1" /> Tour
              </Button>
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

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 pb-24">
        {/* Hero + Tabs */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-white">Welcome, {user.name}!</h1>
            <p className="text-gray-500 text-sm">{new Date().toLocaleDateString('en-IN', { weekday: 'long', month: 'long', day: 'numeric' })}</p>
          </div>
          <div className="flex items-center space-x-2">
            <Button size="sm" className="bg-gradient-to-r from-purple-600 to-pink-600 text-white" onClick={() => setShowWorkspaceModal(true)} data-testid="new-workspace-button"><Plus className="w-4 h-4 mr-1" /> New Workspace</Button>
            <Button size="sm" variant="outline" className="border-gray-700 text-gray-300" onClick={() => setIsDataSourceModalOpen(true)} data-testid="browse-integrations-button"><Upload className="w-4 h-4 mr-1" /> Upload</Button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center space-x-1 bg-gray-900 border border-gray-800 rounded-xl p-1 mb-6 overflow-x-auto" data-testid="dashboard-tabs">
          {[
            { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
            { id: 'notes', label: 'Notes', icon: StickyNote },
            { id: 'reports', label: 'Reports', icon: FileBarChart },
            { id: 'sources', label: 'Data Sources', icon: Database },
          ].map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`flex items-center space-x-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${activeTab === tab.id ? 'bg-purple-600 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800'}`} data-testid={`tab-${tab.id}`}>
              <tab.icon className="w-4 h-4" /><span>{tab.label}</span>
            </button>
          ))}
        </div>

        {/* ===== DASHBOARD TAB ===== */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* Stats Overview */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'Workspaces', value: dashboardSummary?.workspaces ?? workspaces.length, icon: Layers, bg: 'bg-purple-500/10', ic: 'text-purple-400' },
                { label: 'Files Uploaded', value: dashboardSummary?.total_files ?? uploadedFiles.length, icon: FileSpreadsheet, bg: 'bg-emerald-500/10', ic: 'text-emerald-400', badge: dashboardSummary?.recent_files > 0 ? `+${dashboardSummary.recent_files} this week` : null },
                { label: 'AI Queries', value: dashboardSummary?.ai_queries ?? 0, icon: Brain, bg: 'bg-blue-500/10', ic: 'text-blue-400' },
                { label: 'Plan', value: user.plan, icon: CreditCard, bg: 'bg-amber-500/10', ic: 'text-amber-400', isText: true },
              ].map((s, i) => (
                <Card key={i} className="bg-gray-900 border-gray-800" data-testid={`stat-${s.label.toLowerCase().replace(/\s/g, '-')}`}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className={`p-2 rounded-lg ${s.bg}`}><s.icon className={`w-4 h-4 ${s.ic}`} /></div>
                      {s.badge && <span className="text-[10px] bg-emerald-500/10 text-emerald-400 px-1.5 py-0.5 rounded-full">{s.badge}</span>}
                    </div>
                    <p className={`${s.isText ? 'text-lg' : 'text-2xl'} font-bold text-white`}>{s.value}</p>
                    <p className="text-gray-500 text-xs">{s.label}</p>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Auto-Generated Charts for each file */}
            {uploadedFiles.length > 0 ? (
              uploadedFiles.map(file => (
                <div key={file.id} data-testid={`file-charts-${file.id}`}>
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 bg-emerald-500/10 rounded-lg flex items-center justify-center"><FileSpreadsheet className="w-4 h-4 text-emerald-400" /></div>
                      <div>
                        <h3 className="text-white font-semibold text-sm">{file.filename}</h3>
                        <p className="text-gray-500 text-xs">{file.total_rows} rows x {file.total_columns} cols</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button variant="ghost" size="sm" className="text-purple-400 text-xs" onClick={() => handleViewFileDetails(file.id)}><Eye className="w-3 h-3 mr-1" /> Details</Button>
                      <Button variant="ghost" size="sm" className="text-red-400 text-xs" onClick={() => handleDeleteFile(file.id, file.filename)} data-testid={`delete-file-${file.id}`}><Trash2 className="w-3 h-3" /></Button>
                    </div>
                  </div>
                  {chartsData[file.id] ? (
                    <AnalyticsDashboard charts={chartsData[file.id].charts} filename={file.filename} />
                  ) : (
                    <div className="flex items-center justify-center py-8 bg-gray-900 border border-gray-800 rounded-xl">
                      <Loader2 className="w-5 h-5 text-purple-400 animate-spin mr-2" /><span className="text-gray-400 text-sm">Generating charts...</span>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <Card className="bg-gray-900 border-gray-800">
                <CardContent className="py-16 text-center">
                  <div className="w-14 h-14 bg-purple-500/10 rounded-2xl flex items-center justify-center mx-auto mb-4"><BarChart className="w-7 h-7 text-purple-400" /></div>
                  <h3 className="text-white font-semibold mb-1">No analytics yet</h3>
                  <p className="text-gray-500 text-sm mb-4">Upload a CSV or Excel file to auto-generate charts and insights</p>
                  <Button className="bg-gradient-to-r from-purple-600 to-pink-600" onClick={() => setIsDataSourceModalOpen(true)}><Upload className="w-4 h-4 mr-2" /> Upload File</Button>
                </CardContent>
              </Card>
            )}

            {/* Workspaces Grid */}
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-white flex items-center text-base"><Folder className="w-5 h-5 mr-2 text-purple-400" /> Workspaces</CardTitle>
                  <span className="text-xs text-gray-500">{workspaces.length} workspace{workspaces.length !== 1 ? 's' : ''}</span>
                </div>
              </CardHeader>
              <CardContent>
                {workspaces.length === 0 ? (
                  <div className="text-center py-8 border-2 border-dashed border-gray-800 rounded-xl">
                    <Layers className="w-10 h-10 text-gray-700 mx-auto mb-3" />
                    <p className="text-gray-400 mb-2">No workspaces yet</p>
                    <Button size="sm" className="bg-gradient-to-r from-purple-600 to-pink-600" onClick={() => setShowWorkspaceModal(true)}><Plus className="w-3 h-3 mr-1" /> Create Workspace</Button>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    {workspaces.map(ws => (
                      <div key={ws.id} className="group bg-gray-800/40 rounded-xl p-4 border border-gray-700/50 hover:border-purple-500/50 transition-all cursor-pointer" onClick={() => setSelectedWorkspace(ws)} data-testid={`workspace-card-${ws.id}`}>
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <div className="w-8 h-8 bg-purple-500/10 rounded-lg flex items-center justify-center"><Folder className="w-4 h-4 text-purple-400" /></div>
                            <div><h3 className="text-white font-medium text-sm">{ws.name}</h3><p className="text-gray-500 text-xs">{ws.data_sources.length} sources</p></div>
                          </div>
                          <button onClick={(e) => { e.stopPropagation(); handleDeleteWorkspace(ws.id, ws.name); }} className="text-gray-600 hover:text-red-400 opacity-0 group-hover:opacity-100 p-1" data-testid={`delete-workspace-${ws.id}`}><Trash2 className="w-3.5 h-3.5" /></button>
                        </div>
                        <div className="flex flex-wrap gap-1 mb-2">{ws.data_sources.slice(0, 3).map((ds, i) => <span key={i} className="text-[10px] bg-gray-700/60 text-gray-300 px-2 py-0.5 rounded">{ds}</span>)}</div>
                        <p className="text-xs text-purple-400/70 group-hover:text-purple-400 flex items-center">Open<ChevronRight className="w-3 h-3 ml-0.5" /></p>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Recent Activity + Plan */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <div className="lg:col-span-2">
                <Card className="bg-gray-900 border-gray-800">
                  <CardHeader className="pb-3"><CardTitle className="text-white flex items-center text-base"><Activity className="w-5 h-5 mr-2 text-blue-400" /> Recent Activity</CardTitle></CardHeader>
                  <CardContent>
                    {dashboardSummary?.activities?.length > 0 ? (
                      <div className="space-y-3">{dashboardSummary.activities.slice(0, 5).map((act, i) => (
                        <div key={i} className="flex items-start space-x-3">
                          <div className={`w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 ${act.type === 'upload' ? 'bg-emerald-500/10' : act.type === 'workspace' ? 'bg-purple-500/10' : 'bg-blue-500/10'}`}>
                            {act.type === 'upload' ? <Upload className="w-3.5 h-3.5 text-emerald-400" /> : act.type === 'workspace' ? <Folder className="w-3.5 h-3.5 text-purple-400" /> : <Brain className="w-3.5 h-3.5 text-blue-400" />}
                          </div>
                          <div><p className="text-gray-200 text-sm">{act.title}</p><p className="text-gray-600 text-xs">{act.subtitle}{act.time ? ` · ${new Date(act.time).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' })}` : ''}</p></div>
                        </div>
                      ))}</div>
                    ) : <p className="text-gray-600 text-sm text-center py-6">No activity yet</p>}
                  </CardContent>
                </Card>
              </div>
              <Card className="bg-gray-900 border-gray-800 overflow-hidden">
                <div className="h-1 bg-gradient-to-r from-purple-500 via-pink-500 to-purple-500" />
                <CardContent className="p-5">
                  <p className="text-gray-500 text-xs uppercase tracking-wider mb-1">Current Plan</p>
                  <p className="text-xl font-bold text-white mb-4">{user.plan}</p>
                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm"><span className="text-gray-400">Credits</span><span className="text-white">{user.credits}</span></div>
                    <div className="flex justify-between text-sm"><span className="text-gray-400">Status</span><span className="text-emerald-400 capitalize">{user.status}</span></div>
                  </div>
                  <Button className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-sm" onClick={() => setShowUpgradeModal(true)} data-testid="upgrade-plan-button"><ArrowUp className="w-3.5 h-3.5 mr-1" /> Upgrade</Button>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* ===== NOTES TAB ===== */}
        {activeTab === 'notes' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-white">Notes</h2>
              <Button size="sm" className="bg-gradient-to-r from-purple-600 to-pink-600" onClick={() => { setEditingNote(null); setNoteTitle(''); setNoteContent(''); setShowNoteModal(true); }} data-testid="create-note-btn"><Plus className="w-4 h-4 mr-1" /> New Note</Button>
            </div>
            {notes.length === 0 ? (
              <Card className="bg-gray-900 border-gray-800"><CardContent className="py-12 text-center">
                <StickyNote className="w-10 h-10 text-gray-700 mx-auto mb-3" />
                <p className="text-gray-400 mb-2">No notes yet</p>
                <Button size="sm" className="bg-gradient-to-r from-purple-600 to-pink-600" onClick={() => { setNoteTitle(''); setNoteContent(''); setShowNoteModal(true); }}><Plus className="w-3 h-3 mr-1" /> Create Note</Button>
              </CardContent></Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {notes.map(note => (
                  <Card key={note.id} className="bg-gray-900 border-gray-800 group hover:border-gray-700 transition-all">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="text-white font-medium text-sm">{note.title}</h3>
                        <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button onClick={() => { setEditingNote(note.id); setNoteTitle(note.title); setNoteContent(note.content); setShowNoteModal(true); }} className="p-1 text-gray-500 hover:text-white"><Pencil className="w-3 h-3" /></button>
                          <button onClick={() => handleDeleteNote(note.id)} className="p-1 text-gray-500 hover:text-red-400"><Trash2 className="w-3 h-3" /></button>
                        </div>
                      </div>
                      <p className="text-gray-400 text-sm line-clamp-4 whitespace-pre-wrap">{note.content}</p>
                      <p className="text-gray-600 text-xs mt-3">{new Date(note.updated_at).toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' })}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ===== REPORTS TAB ===== */}
        {activeTab === 'reports' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-white">Reports</h2>
              {reports.length > 0 && <Button size="sm" variant="outline" className="border-purple-500 text-purple-400 text-xs" onClick={handleDownloadReport} data-testid="download-reports-button"><Download className="w-3 h-3 mr-1" /> Export All</Button>}
            </div>
            {reports.length === 0 ? (
              <Card className="bg-gray-900 border-gray-800"><CardContent className="py-12 text-center">
                <FileBarChart className="w-10 h-10 text-gray-700 mx-auto mb-3" />
                <p className="text-gray-400 mb-2">No reports yet</p>
                <p className="text-gray-600 text-sm">Upload files to auto-generate reports</p>
              </CardContent></Card>
            ) : (
              <div className="space-y-2">
                {reports.map(r => (
                  <Card key={r.id} className="bg-gray-900 border-gray-800 hover:border-gray-700 transition-all cursor-pointer" onClick={() => { setActiveTab('dashboard'); }}>
                    <CardContent className="p-4 flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-emerald-500/10 rounded-lg flex items-center justify-center"><FileBarChart className="w-5 h-5 text-emerald-400" /></div>
                        <div>
                          <p className="text-white font-medium text-sm">{r.filename}</p>
                          <p className="text-gray-500 text-xs">{r.total_rows} rows x {r.total_columns} cols · {r.source_type}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs text-gray-500">{new Date(r.uploaded_at).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' })}</span>
                        <Button variant="ghost" size="sm" className="text-purple-400 text-xs" onClick={(e) => { e.stopPropagation(); handleViewFileDetails(r.id); }}><Eye className="w-3 h-3 mr-1" /> View</Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ===== DATA SOURCES TAB ===== */}
        {activeTab === 'sources' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-white">Data Sources</h2>
              <Button size="sm" className="bg-gradient-to-r from-purple-600 to-pink-600" onClick={() => setIsDataSourceModalOpen(true)}><Plus className="w-4 h-4 mr-1" /> Connect Source</Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {integrations.map((intg, i) => (
                <Card key={i} className="bg-gray-900 border-gray-800 hover:border-gray-700 transition-all cursor-pointer" onClick={() => handleIntegrationClick(intg)}>
                  <CardContent className="p-4 flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${intg.color}15` }}><Database className="w-5 h-5" style={{ color: intg.color }} /></div>
                    <div className="flex-1"><p className="text-white text-sm font-medium">{intg.name}</p><p className="text-gray-500 text-xs">{intg.type || 'Integration'}</p></div>
                    <ChevronRight className="w-4 h-4 text-gray-600" />
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* AI Chat Bar - Fixed at bottom */}
      <div className="fixed bottom-0 left-0 right-0 z-30 bg-gradient-to-t from-gray-950 via-gray-950 to-transparent pt-6 pb-4 px-4" data-testid="ai-chat-bar">
        <div className="max-w-3xl mx-auto">
          {/* Chat messages popover */}
          {aiChatMessages.length > 0 && (
            <div className="bg-gray-900 border border-gray-800 rounded-t-2xl max-h-[50vh] overflow-y-auto p-4 space-y-3 mb-0">
              {aiChatMessages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] rounded-2xl px-4 py-2.5 ${msg.role === 'user' ? 'bg-purple-600 text-white rounded-tr-sm' : msg.isError ? 'bg-red-900/20 border border-red-800 text-gray-300 rounded-tl-sm' : 'bg-gray-800 text-gray-200 border border-gray-700 rounded-tl-sm'}`}>
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                    {msg.sources?.length > 0 && <div className="mt-1 flex gap-1 flex-wrap">{msg.sources.map((s, si) => <span key={si} className="text-[10px] bg-gray-700 text-gray-400 px-1.5 py-0.5 rounded">{s}</span>)}</div>}
                  </div>
                </div>
              ))}
              {isChatSending && (
                <div className="flex justify-start">
                  <div className="bg-gray-800 border border-gray-700 rounded-2xl rounded-tl-sm px-4 py-2.5">
                    <div className="flex space-x-1.5"><div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" /><div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} /><div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} /></div>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>
          )}
          {/* Chat Input */}
          <div className={`bg-gray-900 border border-gray-700 ${aiChatMessages.length > 0 ? 'rounded-b-2xl border-t-0' : 'rounded-2xl'} overflow-hidden focus-within:border-purple-500/50 transition-colors shadow-xl shadow-black/30`}>
            <div className="flex items-center">
              <Brain className="w-5 h-5 text-purple-400 ml-4 flex-shrink-0" />
              <input value={aiChatInput} onChange={(e) => setAiChatInput(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter') handleDashboardChat(); }} placeholder="Ask anything about your data..." className="flex-1 bg-transparent text-white px-3 py-3.5 outline-none placeholder-gray-500 text-sm" data-testid="dashboard-ai-input" />
              <Button onClick={handleDashboardChat} disabled={isChatSending || !aiChatInput.trim()} className="m-1.5 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl h-8 w-8 p-0" data-testid="dashboard-ai-send">
                {isChatSending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Notes Modal */}
      <Dialog open={showNoteModal} onOpenChange={setShowNoteModal}>
        <DialogContent className="bg-gray-900 border-gray-800 text-white">
          <DialogHeader>
            <DialogTitle>{editingNote ? 'Edit Note' : 'New Note'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div><Label className="text-gray-300 text-sm">Title</Label><Input value={noteTitle} onChange={(e) => setNoteTitle(e.target.value)} placeholder="Note title..." className="bg-gray-800 border-gray-700 text-white mt-1" data-testid="note-title-input" /></div>
            <div><Label className="text-gray-300 text-sm">Content</Label><textarea value={noteContent} onChange={(e) => setNoteContent(e.target.value)} placeholder="Write your notes..." className="w-full bg-gray-800 border border-gray-700 text-white rounded-md p-3 mt-1 outline-none focus:border-purple-500 min-h-[150px] text-sm" data-testid="note-content-input" /></div>
            <div className="flex space-x-3">
              <Button variant="outline" className="flex-1 border-gray-700 text-gray-300" onClick={() => setShowNoteModal(false)}>Cancel</Button>
              <Button className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600" onClick={handleSaveNote} disabled={!noteTitle.trim()} data-testid="save-note-btn"><Save className="w-4 h-4 mr-1" /> Save</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

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
                {['Excel', 'CSV', 'Google Ads', 'Meta Ads', 'Google Sheets', 'Zoho Books', 'Google Analytics', 'Zoho CRM', 'Notion API', 'Practo API', 'Shopify'].map(ds => (
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
