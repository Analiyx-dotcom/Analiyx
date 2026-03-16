import React, { useEffect, useState, useCallback, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { ArrowLeft, Send, Brain, X, Upload, FileSpreadsheet, Loader2, CheckCircle, Database, Download, Trash2, Plus, BarChart, MessageCircle, User, Sparkles, ChevronDown } from 'lucide-react';
import { dataSourceAPI } from '../services/api';
import api from '../services/api';
import { toast } from '../hooks/use-toast';
import { integrations } from '../mock/mockData';
import { exportFilesToExcel } from '../utils/reportExport';

const WorkspaceView = ({ workspace, onBack, user }) => {
  const [files, setFiles] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [showIntegrations, setShowIntegrations] = useState(false);
  const [fileDetails, setFileDetails] = useState(null);
  const [showFileDetails, setShowFileDetails] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const chatEndRef = useRef(null);
  const chatInputRef = useRef(null);

  const fetchFiles = useCallback(async () => {
    try {
      const data = await dataSourceAPI.getUploadedFiles(workspace.id);
      setFiles(data.files || []);
    } catch { }
  }, [workspace.id]);

  // Load chat history
  const loadChatHistory = useCallback(async () => {
    try {
      const res = await api.get(`/ai/chat/history/${workspace.id}`);
      if (res.data.history?.length > 0) {
        setChatMessages(res.data.history);
      }
    } catch { }
  }, [workspace.id]);

  useEffect(() => { fetchFiles(); loadChatHistory(); }, [fetchFiles, loadChatHistory]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const handleSendMessage = async () => {
    if (!chatInput.trim() || isSending) return;
    const userMsg = chatInput.trim();
    setChatInput('');
    setChatMessages(prev => [...prev, { role: 'user', content: userMsg, timestamp: new Date().toISOString() }]);
    setIsSending(true);

    try {
      const res = await api.post('/ai/chat', {
        query: userMsg,
        workspace_id: workspace.id,
        session_id: sessionId
      });
      if (res.data.session_id) setSessionId(res.data.session_id);
      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: res.data.answer,
        sources: res.data.sources,
        timestamp: new Date().toISOString()
      }]);
    } catch (error) {
      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
        isError: true
      }]);
      toast({ title: 'Chat Error', description: typeof error.response?.data?.detail === 'string' ? error.response.data.detail : 'Failed to get AI response. Please try again.', variant: 'destructive' });
    } finally { setIsSending(false); setTimeout(() => chatInputRef.current?.focus(), 100); }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSendMessage(); }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.name.match(/\.(csv|xlsx|xls)$/i)) {
        toast({ title: 'Invalid file', description: 'CSV or Excel only.', variant: 'destructive' });
        return;
      }
      setSelectedFile(file);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    try {
      await dataSourceAPI.uploadFile(selectedFile, workspace.id);
      toast({ title: 'Uploaded!', description: `${selectedFile.name} added to ${workspace.name}` });
      setSelectedFile(null);
      setShowFileUpload(false);
      setShowIntegrations(false);
      fetchFiles();
    } catch (error) {
      toast({ title: 'Upload failed', description: typeof error.response?.data?.detail === 'string' ? error.response.data.detail : 'Upload error', variant: 'destructive' });
    } finally { setIsUploading(false); }
  };

  const handleDeleteFile = async (fileId, filename) => {
    if (!window.confirm(`Delete "${filename}"?`)) return;
    try {
      await dataSourceAPI.deleteFile(fileId);
      toast({ title: 'Deleted', description: `${filename} removed.` });
      fetchFiles();
    } catch { toast({ title: 'Error', description: 'Failed to delete.', variant: 'destructive' }); }
  };

  const handleViewFileDetails = async (fileId) => {
    try {
      const data = await dataSourceAPI.getFileDetails(fileId);
      setFileDetails(data);
      setShowFileDetails(true);
    } catch { toast({ title: 'Error', description: 'Could not load file.', variant: 'destructive' }); }
  };

  const handleIntegrationClick = (integration) => {
    if (integration.name === 'Excel' || integration.name === 'CSV') {
      setShowFileUpload(true);
    } else {
      toast({ title: 'Coming Soon', description: `${integration.name} integration coming soon!` });
    }
  };

  const wsIntegrations = integrations.filter(i => workspace.data_sources.includes(i.name));
  const otherIntegrations = integrations.filter(i => !workspace.data_sources.includes(i.name));

  // Render markdown-like text
  const renderMessage = (text) => {
    if (!text) return null;
    return text.split('\n').map((line, i) => {
      // Bold
      let processed = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      // Headers
      if (line.startsWith('#### ')) return <h4 key={i} className="text-white font-semibold text-sm mt-3 mb-1" dangerouslySetInnerHTML={{ __html: processed.slice(5) }} />;
      if (line.startsWith('### ')) return <h3 key={i} className="text-white font-semibold mt-3 mb-1" dangerouslySetInnerHTML={{ __html: processed.slice(4) }} />;
      if (line.startsWith('## ')) return <h2 key={i} className="text-white font-bold text-lg mt-4 mb-2" dangerouslySetInnerHTML={{ __html: processed.slice(3) }} />;
      // Bullets
      if (line.startsWith('- ')) return <li key={i} className="text-gray-300 text-sm ml-4 list-disc" dangerouslySetInnerHTML={{ __html: processed.slice(2) }} />;
      // Horizontal rule
      if (line.trim() === '---') return <hr key={i} className="border-gray-700 my-3" />;
      // Empty line
      if (line.trim() === '') return <div key={i} className="h-2" />;
      // Regular text
      return <p key={i} className="text-gray-300 text-sm" dangerouslySetInnerHTML={{ __html: processed }} />;
    });
  };

  const quickPrompts = [
    "Summarize my data",
    "What insights can you find?",
    "Show key statistics",
    "Are there any issues in my data?",
  ];

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      {/* Header */}
      <div className="bg-gray-900 border-b border-gray-800 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center">
              <button onClick={onBack} className="flex items-center text-gray-400 hover:text-white transition-colors mr-4" data-testid="workspace-back-button">
                <ArrowLeft className="w-5 h-5 mr-1" /> Back
              </button>
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                  <Database className="w-4 h-4 text-white" />
                </div>
                <div>
                  <h1 className="text-lg font-bold text-white leading-tight" data-testid="workspace-title">{workspace.name}</h1>
                  <p className="text-xs text-gray-500">{workspace.data_sources.length} source{workspace.data_sources.length !== 1 ? 's' : ''} · {files.length} file{files.length !== 1 ? 's' : ''}</p>
                </div>
              </div>
            </div>
            {/* Tab Switcher */}
            <div className="flex items-center bg-gray-800 rounded-lg p-0.5">
              <button onClick={() => setActiveTab('chat')} className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${activeTab === 'chat' ? 'bg-purple-600 text-white' : 'text-gray-400 hover:text-white'}`} data-testid="ws-tab-chat">
                <MessageCircle className="w-3.5 h-3.5 inline mr-1" /> AI Chat
              </button>
              <button onClick={() => setActiveTab('files')} className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${activeTab === 'files' ? 'bg-purple-600 text-white' : 'text-gray-400 hover:text-white'}`} data-testid="ws-tab-files">
                <FileSpreadsheet className="w-3.5 h-3.5 inline mr-1" /> Files ({files.length})
              </button>
              <button onClick={() => setActiveTab('sources')} className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${activeTab === 'sources' ? 'bg-purple-600 text-white' : 'text-gray-400 hover:text-white'}`} data-testid="ws-tab-sources">
                <Database className="w-3.5 h-3.5 inline mr-1" /> Sources
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      {activeTab === 'chat' && (
        <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full px-4">
          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto py-6 space-y-4" style={{ maxHeight: 'calc(100vh - 180px)' }} data-testid="ws-chat-messages">
            {chatMessages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full pt-16">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-2xl flex items-center justify-center mb-5">
                  <Brain className="w-8 h-8 text-purple-400" />
                </div>
                <h2 className="text-xl font-bold text-white mb-2">Ask anything about your data</h2>
                <p className="text-gray-500 text-sm mb-8 text-center max-w-md">I have access to all files in <span className="text-purple-400">{workspace.name}</span>. Ask me questions, request analysis, or explore insights.</p>
                <div className="grid grid-cols-2 gap-2 w-full max-w-md">
                  {quickPrompts.map((prompt, i) => (
                    <button key={i} onClick={() => { setChatInput(prompt); setTimeout(() => chatInputRef.current?.focus(), 50); }} className="text-left bg-gray-900 border border-gray-800 rounded-xl p-3 hover:border-purple-500/50 hover:bg-gray-800/50 transition-all group" data-testid={`quick-prompt-${i}`}>
                      <p className="text-gray-300 text-sm group-hover:text-white transition-colors">{prompt}</p>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <>
                {chatMessages.map((msg, i) => (
                  <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`} data-testid={`chat-message-${i}`}>
                    <div className={`max-w-[85%] ${msg.role === 'user' ? 'order-2' : 'order-1'}`}>
                      <div className={`flex items-start space-x-2.5 ${msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                        {/* Avatar */}
                        <div className={`w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5 ${msg.role === 'user' ? 'bg-purple-600' : msg.isError ? 'bg-red-500/20' : 'bg-gradient-to-br from-purple-500/20 to-pink-500/20'}`}>
                          {msg.role === 'user' ? <User className="w-3.5 h-3.5 text-white" /> : <Brain className="w-3.5 h-3.5 text-purple-400" />}
                        </div>
                        {/* Message Bubble */}
                        <div className={`rounded-2xl px-4 py-3 ${msg.role === 'user' ? 'bg-purple-600 text-white rounded-tr-sm' : msg.isError ? 'bg-red-900/20 border border-red-800 rounded-tl-sm' : 'bg-gray-900 border border-gray-800 rounded-tl-sm'}`}>
                          {msg.role === 'user' ? (
                            <p className="text-sm">{msg.content}</p>
                          ) : (
                            <div className="prose-sm">{renderMessage(msg.content)}</div>
                          )}
                          {msg.sources?.length > 0 && (
                            <div className="mt-2 pt-2 border-t border-gray-800 flex items-center gap-1.5 flex-wrap">
                              <span className="text-[10px] text-gray-600">Sources:</span>
                              {msg.sources.map((s, si) => <span key={si} className="text-[10px] bg-gray-800 text-gray-500 px-1.5 py-0.5 rounded">{s}</span>)}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                {isSending && (
                  <div className="flex justify-start" data-testid="chat-typing-indicator">
                    <div className="flex items-start space-x-2.5">
                      <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <Brain className="w-3.5 h-3.5 text-purple-400" />
                      </div>
                      <div className="bg-gray-900 border border-gray-800 rounded-2xl rounded-tl-sm px-4 py-3">
                        <div className="flex items-center space-x-1.5">
                          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </>
            )}
          </div>

          {/* Chat Input */}
          <div className="sticky bottom-0 bg-gray-950 pb-4 pt-2">
            <div className="bg-gray-900 border border-gray-700 rounded-2xl overflow-hidden focus-within:border-purple-500/50 transition-colors shadow-lg shadow-black/20">
              <div className="flex items-end">
                <textarea
                  ref={chatInputRef}
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={`Ask about your ${workspace.name} data...`}
                  className="flex-1 bg-transparent text-white px-4 py-3 outline-none placeholder-gray-500 resize-none text-sm min-h-[44px] max-h-[120px]"
                  rows={1}
                  data-testid="ws-chat-input"
                />
                <Button onClick={handleSendMessage} disabled={isSending || !chatInput.trim()} className="m-1.5 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-xl h-9 w-9 p-0" data-testid="ws-chat-send">
                  {isSending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                </Button>
              </div>
            </div>
            <p className="text-center text-[10px] text-gray-600 mt-2">AI responses are based on your uploaded data. Results may vary.</p>
          </div>
        </div>
      )}

      {activeTab === 'files' && (
        <main className="max-w-4xl mx-auto w-full px-4 py-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white">Files in {workspace.name}</h2>
            <Button size="sm" className="bg-gradient-to-r from-purple-600 to-pink-600 text-xs" onClick={() => { setShowIntegrations(true); setShowFileUpload(true); }} data-testid="ws-upload-file">
              <Upload className="w-3 h-3 mr-1" /> Upload File
            </Button>
          </div>
          {files.length === 0 ? (
            <Card className="bg-gray-900 border-gray-800">
              <CardContent className="py-12 text-center">
                <Upload className="w-10 h-10 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-400 mb-1">No files yet</p>
                <p className="text-gray-600 text-sm mb-4">Upload CSV or Excel files to analyze</p>
                <Button size="sm" className="bg-gradient-to-r from-purple-600 to-pink-600" onClick={() => { setShowIntegrations(true); setShowFileUpload(true); }}>
                  <Upload className="w-4 h-4 mr-2" /> Upload File
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-2">
              {files.length > 0 && (
                <div className="flex justify-end mb-2">
                  <Button variant="ghost" size="sm" className="text-purple-400 text-xs" onClick={() => { exportFilesToExcel(files, null); toast({ title: 'Exported!' }); }} data-testid="ws-download-reports">
                    <Download className="w-3 h-3 mr-1" /> Export All
                  </Button>
                </div>
              )}
              {files.map((file) => (
                <div key={file.id} className="flex items-center justify-between p-3 bg-gray-900 border border-gray-800 rounded-xl hover:border-gray-700 transition-colors group">
                  <div className="flex items-center space-x-3 cursor-pointer flex-1" onClick={() => handleViewFileDetails(file.id)}>
                    <div className="w-9 h-9 bg-emerald-500/10 rounded-lg flex items-center justify-center"><CheckCircle className="w-4 h-4 text-emerald-500" /></div>
                    <div>
                      <p className="text-white font-medium text-sm">{file.filename}</p>
                      <p className="text-gray-500 text-xs">{file.total_rows} rows x {file.total_columns} cols</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button variant="ghost" size="sm" className="text-purple-400 text-xs h-7" onClick={() => handleViewFileDetails(file.id)}><BarChart className="w-3 h-3" /></Button>
                    <Button variant="ghost" size="sm" className="text-red-400 hover:bg-red-900/20 h-7" onClick={() => handleDeleteFile(file.id, file.filename)} data-testid={`ws-delete-file-${file.id}`}><Trash2 className="w-3 h-3" /></Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      )}

      {activeTab === 'sources' && (
        <main className="max-w-4xl mx-auto w-full px-4 py-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white">Data Sources</h2>
            <Button size="sm" variant="outline" className="border-purple-500 text-purple-400 text-xs" onClick={() => setShowIntegrations(true)} data-testid="ws-add-integration">
              <Plus className="w-3 h-3 mr-1" /> Add Source
            </Button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {workspace.data_sources.map((ds, i) => (
              <Card key={i} className="bg-gray-900 border-gray-800">
                <CardContent className="p-4 flex items-center space-x-3">
                  <div className="w-10 h-10 bg-purple-500/10 rounded-lg flex items-center justify-center"><Database className="w-5 h-5 text-purple-400" /></div>
                  <div className="flex-1">
                    <p className="text-white font-medium text-sm">{ds}</p>
                    <p className="text-gray-500 text-xs">Connected</p>
                  </div>
                  <CheckCircle className="w-4 h-4 text-emerald-500" />
                </CardContent>
              </Card>
            ))}
          </div>
        </main>
      )}

      {/* Integration / File Upload Modal */}
      <Dialog open={showIntegrations} onOpenChange={(v) => { setShowIntegrations(v); if (!v) setShowFileUpload(false); }}>
        <DialogContent className="bg-gray-900 border-gray-800 text-white max-w-3xl">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold">{showFileUpload ? 'Upload File' : 'Connect Data Source'}</DialogTitle>
            <DialogDescription className="text-gray-400">{showFileUpload ? `Upload to ${workspace.name}` : 'Choose a data source'}</DialogDescription>
          </DialogHeader>
          {showFileUpload ? (
            <div className="py-4">
              <div className="border-2 border-dashed border-gray-700 rounded-xl p-8 text-center hover:border-purple-500 transition-colors">
                <input type="file" accept=".csv,.xlsx,.xls" onChange={handleFileSelect} className="hidden" id="ws-file-upload" />
                <label htmlFor="ws-file-upload" className="cursor-pointer">
                  <Upload className="w-10 h-10 text-gray-400 mx-auto mb-3" />
                  <p className="text-white font-semibold mb-1">{selectedFile ? selectedFile.name : 'Click to upload'}</p>
                  <p className="text-gray-400 text-sm">CSV or Excel (max 10MB)</p>
                </label>
              </div>
              {selectedFile && (
                <div className="mt-3 bg-gray-800 rounded-lg p-3 flex items-center justify-between">
                  <div className="flex items-center space-x-3"><FileSpreadsheet className="w-6 h-6 text-emerald-500" /><div><p className="text-white text-sm">{selectedFile.name}</p><p className="text-gray-400 text-xs">{(selectedFile.size / 1024).toFixed(1)} KB</p></div></div>
                  <Button variant="ghost" size="sm" onClick={() => setSelectedFile(null)} className="text-gray-400"><X className="w-4 h-4" /></Button>
                </div>
              )}
              <div className="flex space-x-3 mt-4">
                <Button variant="outline" className="flex-1 border-gray-700 text-gray-300" onClick={() => { setShowFileUpload(false); setSelectedFile(null); }}>Back</Button>
                <Button className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600" onClick={handleFileUpload} disabled={!selectedFile || isUploading}>
                  {isUploading ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Uploading...</> : <><Upload className="w-4 h-4 mr-2" />Upload & Analyze</>}
                </Button>
              </div>
            </div>
          ) : (
            <div className="py-4">
              {wsIntegrations.length > 0 && (
                <div className="mb-4">
                  <p className="text-xs text-gray-500 mb-2 uppercase tracking-wider">Workspace Sources</p>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {wsIntegrations.map((integration, i) => (
                      <button key={i} className="group bg-gray-800 border border-purple-500/40 rounded-xl p-3 hover:border-purple-500 transition-all" onClick={() => handleIntegrationClick(integration)}>
                        <div className="flex flex-col items-center space-y-2">
                          <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${integration.color}20` }}><Database className="w-5 h-5" style={{ color: integration.color }} /></div>
                          <span className="text-xs text-gray-300">{integration.name}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
              {otherIntegrations.length > 0 && (
                <div>
                  <p className="text-xs text-gray-500 mb-2 uppercase tracking-wider">Other Integrations</p>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {otherIntegrations.map((integration, i) => (
                      <button key={i} className="group bg-gray-800 border border-gray-700 rounded-xl p-3 hover:border-gray-600 transition-all" onClick={() => handleIntegrationClick(integration)}>
                        <div className="flex flex-col items-center space-y-2">
                          <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${integration.color}20` }}><Database className="w-5 h-5" style={{ color: integration.color }} /></div>
                          <span className="text-xs text-gray-400">{integration.name}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* File Details Modal */}
      <Dialog open={showFileDetails} onOpenChange={setShowFileDetails}>
        <DialogContent className="bg-gray-900 border-gray-800 text-white max-w-5xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold">File Analytics</DialogTitle>
            <DialogDescription className="text-gray-400">{fileDetails?.filename}</DialogDescription>
          </DialogHeader>
          {fileDetails && (
            <div className="space-y-6 py-4">
              <div className="grid grid-cols-3 gap-4">
                <Card className="bg-gray-800 border-gray-700"><CardContent className="p-4 text-center"><p className="text-gray-400 text-sm">Rows</p><p className="text-3xl font-bold text-purple-400">{fileDetails.analytics.total_rows.toLocaleString()}</p></CardContent></Card>
                <Card className="bg-gray-800 border-gray-700"><CardContent className="p-4 text-center"><p className="text-gray-400 text-sm">Columns</p><p className="text-3xl font-bold text-blue-400">{fileDetails.analytics.total_columns}</p></CardContent></Card>
                <Card className="bg-gray-800 border-gray-700"><CardContent className="p-4 text-center"><p className="text-gray-400 text-sm">Type</p><p className="text-3xl font-bold text-emerald-400">{fileDetails.source_type}</p></CardContent></Card>
              </div>
              <Card className="bg-gray-800 border-gray-700">
                <CardHeader><CardTitle className="text-white text-lg">Column Data Types</CardTitle></CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(fileDetails.analytics.columns.reduce((acc, col) => { const t = fileDetails.analytics.data_types[col] || 'unknown'; acc[t] = (acc[t] || 0) + 1; return acc; }, {})).map(([type, count], i) => {
                      const colors = ['bg-purple-500', 'bg-blue-500', 'bg-emerald-500', 'bg-amber-500', 'bg-pink-500'];
                      const pct = Math.round((count / fileDetails.analytics.total_columns) * 100);
                      return (
                        <div key={type}>
                          <div className="flex justify-between text-sm mb-1"><span className="text-gray-300">{type}</span><span className="text-gray-400">{count} ({pct}%)</span></div>
                          <div className="w-full bg-gray-700 rounded-full h-2.5"><div className={`${colors[i % colors.length]} h-2.5 rounded-full`} style={{ width: `${pct}%` }} /></div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
              {fileDetails.analytics.numeric_summary && Object.keys(fileDetails.analytics.numeric_summary).length > 0 && (
                <Card className="bg-gray-800 border-gray-700">
                  <CardHeader><CardTitle className="text-white text-lg">Numeric Statistics</CardTitle></CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {Object.entries(fileDetails.analytics.numeric_summary).map(([col, stats]) => (
                        <div key={col} className="bg-gray-700/50 rounded-lg p-3">
                          <div className="flex justify-between mb-1"><span className="text-white text-sm font-medium">{col}</span><span className="text-gray-400 text-xs">Mean: {typeof stats.mean === 'number' ? stats.mean.toFixed(2) : 'N/A'}</span></div>
                          <div className="relative w-full bg-gray-600 rounded-full h-3"><div className="absolute left-0 top-0 h-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full" style={{ width: `${Math.min(((stats.mean - stats.min) / ((stats.max - stats.min) || 1)) * 100, 100)}%` }} /></div>
                          <div className="flex justify-between text-xs text-gray-500 mt-1"><span>Min: {typeof stats.min === 'number' ? stats.min.toFixed(2) : stats.min}</span><span>Max: {typeof stats.max === 'number' ? stats.max.toFixed(2) : stats.max}</span></div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
              {fileDetails.sample_data?.length > 0 && (
                <Card className="bg-gray-800 border-gray-700">
                  <CardHeader><CardTitle className="text-white text-lg">Sample Data</CardTitle></CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead><tr className="border-b border-gray-700">{Object.keys(fileDetails.sample_data[0]).map((k, i) => <th key={i} className="text-left py-2 px-3 text-gray-400">{k}</th>)}</tr></thead>
                        <tbody>{fileDetails.sample_data.map((row, i) => <tr key={i} className="border-b border-gray-700">{Object.values(row).map((v, vi) => <td key={vi} className="py-2 px-3 text-gray-300">{String(v)}</td>)}</tr>)}</tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default WorkspaceView;
