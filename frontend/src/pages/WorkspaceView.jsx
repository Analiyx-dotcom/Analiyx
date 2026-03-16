import React, { useEffect, useState, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { ArrowLeft, Search, Zap, Brain, X, Upload, FileSpreadsheet, Loader2, CheckCircle, Database, Download, Trash2, Plus, BarChart, Globe } from 'lucide-react';
import { dataSourceAPI } from '../services/api';
import api from '../services/api';
import { toast } from '../hooks/use-toast';
import { integrations } from '../mock/mockData';
import { downloadComprehensiveReport, exportFilesToExcel } from '../utils/reportExport';

const WorkspaceView = ({ workspace, onBack, user }) => {
  const [files, setFiles] = useState([]);
  const [aiSearchQuery, setAiSearchQuery] = useState('');
  const [aiSearchResult, setAiSearchResult] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [showIntegrations, setShowIntegrations] = useState(false);
  const [fileDetails, setFileDetails] = useState(null);
  const [showFileDetails, setShowFileDetails] = useState(false);

  const fetchFiles = useCallback(async () => {
    try {
      const data = await dataSourceAPI.getUploadedFiles(workspace.id);
      setFiles(data.files || []);
    } catch { }
  }, [workspace.id]);

  useEffect(() => { fetchFiles(); }, [fetchFiles]);

  const handleAiSearch = async () => {
    if (!aiSearchQuery.trim()) return;
    setIsSearching(true);
    try {
      const res = await api.post('/ai/search', { query: aiSearchQuery, workspace_id: workspace.id });
      setAiSearchResult(res.data);
    } catch (error) {
      toast({ title: 'Search Failed', description: error.response?.data?.detail || 'AI search failed', variant: 'destructive' });
    } finally { setIsSearching(false); }
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
      await dataSourceAPI.uploadFile(selectedFile, workspace.id);
      toast({ title: 'File uploaded!', description: `Added to ${workspace.name}` });
      setSelectedFile(null);
      setShowFileUpload(false);
      setShowIntegrations(false);
      fetchFiles();
    } catch (error) {
      toast({ title: 'Upload failed', description: error.response?.data?.detail || 'Failed to upload', variant: 'destructive' });
    } finally { setIsUploading(false); }
  };

  const handleDeleteFile = async (fileId, filename) => {
    if (!window.confirm(`Delete "${filename}"?`)) return;
    try {
      await dataSourceAPI.deleteFile(fileId);
      toast({ title: 'Deleted', description: `${filename} removed.` });
      fetchFiles();
    } catch { toast({ title: 'Error', description: 'Failed to delete file.', variant: 'destructive' }); }
  };

  const handleViewFileDetails = async (fileId) => {
    try {
      const data = await dataSourceAPI.getFileDetails(fileId);
      setFileDetails(data);
      setShowFileDetails(true);
    } catch { toast({ title: 'Error', description: 'Could not load file details.', variant: 'destructive' }); }
  };

  const handleIntegrationClick = (integration) => {
    if (integration.name === 'Excel' || integration.name === 'CSV') {
      setShowFileUpload(true);
    } else {
      toast({ title: 'Coming Soon', description: `${integration.name} integration will be available soon!` });
    }
  };

  const handleDownloadReport = () => {
    if (!files.length) { toast({ title: 'No Data', description: 'Upload files first.', variant: 'destructive' }); return; }
    exportFilesToExcel(files, null);
    toast({ title: 'Report Downloaded!' });
  };

  // Filter integrations to only those selected for this workspace
  const wsIntegrations = integrations.filter(i => workspace.data_sources.includes(i.name));
  const otherIntegrations = integrations.filter(i => !workspace.data_sources.includes(i.name));

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Header */}
      <div className="bg-gray-900 border-b border-gray-800 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-14">
            <button onClick={onBack} className="flex items-center text-gray-400 hover:text-white transition-colors mr-4" data-testid="workspace-back-button">
              <ArrowLeft className="w-5 h-5 mr-1" /> Back
            </button>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <Database className="w-4 h-4 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-white leading-tight" data-testid="workspace-title">{workspace.name}</h1>
                <p className="text-xs text-gray-500">{workspace.data_sources.length} data source{workspace.data_sources.length !== 1 ? 's' : ''} connected</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Data Sources Strip */}
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-gray-300">Connected Data Sources</h3>
              <Button size="sm" variant="outline" className="border-purple-500 text-purple-400 hover:bg-purple-900/20 text-xs" onClick={() => setShowIntegrations(true)} data-testid="ws-add-integration">
                <Plus className="w-3 h-3 mr-1" /> Add Source
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {workspace.data_sources.map((ds, i) => (
                <div key={i} className="flex items-center space-x-2 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2">
                  <Database className="w-4 h-4 text-purple-400" />
                  <span className="text-sm text-gray-200">{ds}</span>
                  <CheckCircle className="w-3 h-3 text-green-500" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* AI Search Bar */}
        <div data-testid="ws-ai-search-bar">
          <div className="flex items-center bg-gray-900 border border-gray-700 rounded-xl overflow-hidden focus-within:border-purple-500 transition-colors">
            <Search className="w-5 h-5 text-gray-400 ml-4" />
            <input
              value={aiSearchQuery}
              onChange={(e) => setAiSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAiSearch()}
              placeholder={`Ask about your ${workspace.name} data...`}
              className="flex-1 bg-transparent text-white px-4 py-3 outline-none placeholder-gray-500"
              data-testid="ws-ai-search-input"
            />
            <Button onClick={handleAiSearch} disabled={isSearching || !aiSearchQuery.trim()} className="m-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-lg" data-testid="ws-ai-search-submit">
              {isSearching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
            </Button>
          </div>
          {aiSearchResult && (
            <Card className="bg-gray-900 border-gray-700 mt-3">
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2"><Brain className="w-5 h-5 text-purple-400" /><span className="text-sm font-medium text-purple-400">AI Response</span></div>
                  <button onClick={() => setAiSearchResult(null)} className="text-gray-500 hover:text-white"><X className="w-4 h-4" /></button>
                </div>
                <p className="text-gray-200 text-sm whitespace-pre-wrap">{aiSearchResult.answer}</p>
                {aiSearchResult.sources?.length > 0 && (
                  <div className="mt-3 flex items-center gap-2 flex-wrap">
                    <span className="text-xs text-gray-500">Sources:</span>
                    {aiSearchResult.sources.map((s, i) => <span key={i} className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded">{s}</span>)}
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Files Section */}
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-white flex items-center text-base"><FileSpreadsheet className="w-5 h-5 mr-2" /> Files in {workspace.name}</CardTitle>
              <div className="flex items-center space-x-2">
                {files.length > 0 && (
                  <Button variant="outline" size="sm" onClick={handleDownloadReport} className="border-purple-500 text-purple-400 hover:bg-purple-900/20 text-xs" data-testid="ws-download-reports">
                    <Download className="w-3 h-3 mr-1" /> Export
                  </Button>
                )}
                <Button size="sm" className="bg-gradient-to-r from-purple-600 to-pink-600 text-xs" onClick={() => { setShowIntegrations(true); setShowFileUpload(true); }} data-testid="ws-upload-file">
                  <Upload className="w-3 h-3 mr-1" /> Upload File
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {files.length === 0 ? (
              <div className="text-center py-10">
                <Upload className="w-10 h-10 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-400 mb-1">No files uploaded yet</p>
                <p className="text-gray-600 text-sm mb-4">Upload CSV or Excel files to start analyzing your data</p>
                <Button size="sm" className="bg-gradient-to-r from-purple-600 to-pink-600" onClick={() => { setShowIntegrations(true); setShowFileUpload(true); }}>
                  <Upload className="w-4 h-4 mr-2" /> Upload Your First File
                </Button>
              </div>
            ) : (
              <div className="space-y-2">
                {files.map((file) => (
                  <div key={file.id} className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition-colors">
                    <div className="flex items-center space-x-3 cursor-pointer flex-1" onClick={() => handleViewFileDetails(file.id)}>
                      <div className="w-9 h-9 bg-green-900/20 rounded-lg flex items-center justify-center"><CheckCircle className="w-4 h-4 text-green-500" /></div>
                      <div>
                        <p className="text-white font-medium text-sm">{file.filename}</p>
                        <p className="text-gray-500 text-xs">{file.total_rows} rows x {file.total_columns} cols</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button variant="ghost" size="sm" className="text-purple-400 hover:text-purple-300 text-xs" onClick={() => handleViewFileDetails(file.id)}>
                        <BarChart className="w-3 h-3 mr-1" /> Analytics
                      </Button>
                      <Button variant="ghost" size="sm" className="text-red-400 hover:text-red-300 hover:bg-red-900/20" onClick={() => handleDeleteFile(file.id, file.filename)} data-testid={`ws-delete-file-${file.id}`}>
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card className="bg-gradient-to-br from-purple-900/20 to-pink-900/20 border-purple-500/30 cursor-pointer hover:border-purple-500/60 transition-colors" onClick={() => setShowIntegrations(true)}>
            <CardContent className="p-6 flex items-center space-x-4">
              <div className="p-3 bg-purple-900/30 rounded-xl"><Database className="w-6 h-6 text-purple-400" /></div>
              <div>
                <h3 className="text-white font-medium">Connect More Sources</h3>
                <p className="text-gray-400 text-sm">Add integrations to enrich your analytics</p>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-gradient-to-br from-blue-900/20 to-cyan-900/20 border-blue-500/30 cursor-pointer hover:border-blue-500/60 transition-colors" onClick={() => document.querySelector('[data-testid="ws-ai-search-input"]')?.focus()}>
            <CardContent className="p-6 flex items-center space-x-4">
              <div className="p-3 bg-blue-900/30 rounded-xl"><Brain className="w-6 h-6 text-blue-400" /></div>
              <div>
                <h3 className="text-white font-medium">Ask AI About Your Data</h3>
                <p className="text-gray-400 text-sm">Get insights using natural language queries</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Integration / File Upload Modal */}
      <Dialog open={showIntegrations} onOpenChange={(v) => { setShowIntegrations(v); if (!v) setShowFileUpload(false); }}>
        <DialogContent className="bg-gray-900 border-gray-800 text-white max-w-3xl">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold">{showFileUpload ? 'Upload File' : 'Connect Data Source'}</DialogTitle>
            <DialogDescription className="text-gray-400">{showFileUpload ? `Upload to ${workspace.name}` : 'Choose a data source to connect'}</DialogDescription>
          </DialogHeader>
          {showFileUpload ? (
            <div className="py-4">
              <div className="border-2 border-dashed border-gray-700 rounded-xl p-8 text-center hover:border-purple-500 transition-colors">
                <input type="file" accept=".csv,.xlsx,.xls" onChange={handleFileSelect} className="hidden" id="ws-file-upload" />
                <label htmlFor="ws-file-upload" className="cursor-pointer">
                  <Upload className="w-10 h-10 text-gray-400 mx-auto mb-3" />
                  <p className="text-white font-semibold mb-1">{selectedFile ? selectedFile.name : 'Click to upload'}</p>
                  <p className="text-gray-400 text-sm">CSV or Excel files (max 10MB)</p>
                </label>
              </div>
              {selectedFile && (
                <div className="mt-3 bg-gray-800 rounded-lg p-3 flex items-center justify-between">
                  <div className="flex items-center space-x-3"><FileSpreadsheet className="w-6 h-6 text-green-500" /><div><p className="text-white text-sm">{selectedFile.name}</p><p className="text-gray-400 text-xs">{(selectedFile.size / 1024).toFixed(1)} KB</p></div></div>
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
                          <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${integration.color}20` }}>
                            <Database className="w-5 h-5" style={{ color: integration.color }} />
                          </div>
                          <span className="text-xs text-gray-300 text-center">{integration.name}</span>
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
                          <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${integration.color}20` }}>
                            <Database className="w-5 h-5" style={{ color: integration.color }} />
                          </div>
                          <span className="text-xs text-gray-400 text-center">{integration.name}</span>
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
                <Card className="bg-gray-800 border-gray-700"><CardContent className="p-4 text-center"><p className="text-gray-400 text-sm">Type</p><p className="text-3xl font-bold text-green-400">{fileDetails.source_type}</p></CardContent></Card>
              </div>
              {/* Column Data Types */}
              <Card className="bg-gray-800 border-gray-700">
                <CardHeader><CardTitle className="text-white text-lg">Column Data Types</CardTitle></CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(
                      fileDetails.analytics.columns.reduce((acc, col) => {
                        const type = fileDetails.analytics.data_types[col] || 'unknown';
                        acc[type] = (acc[type] || 0) + 1;
                        return acc;
                      }, {})
                    ).map(([type, count], i) => {
                      const colors = ['bg-purple-500', 'bg-blue-500', 'bg-green-500', 'bg-yellow-500', 'bg-pink-500'];
                      const pct = Math.round((count / fileDetails.analytics.total_columns) * 100);
                      return (
                        <div key={type}>
                          <div className="flex justify-between text-sm mb-1"><span className="text-gray-300">{type}</span><span className="text-gray-400">{count} ({pct}%)</span></div>
                          <div className="w-full bg-gray-700 rounded-full h-2.5"><div className={`${colors[i % colors.length]} h-2.5 rounded-full`} style={{ width: `${pct}%` }}></div></div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
              {/* Numeric Stats */}
              {fileDetails.analytics.numeric_summary && Object.keys(fileDetails.analytics.numeric_summary).length > 0 && (
                <Card className="bg-gray-800 border-gray-700">
                  <CardHeader><CardTitle className="text-white text-lg">Numeric Statistics</CardTitle></CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {Object.entries(fileDetails.analytics.numeric_summary).map(([col, stats]) => {
                        const mean = stats.mean || 0;
                        const min = stats.min || 0;
                        const max = stats.max || 1;
                        const range = max - min || 1;
                        const pct = ((mean - min) / range) * 100;
                        return (
                          <div key={col} className="bg-gray-700/50 rounded-lg p-3">
                            <div className="flex justify-between mb-1"><span className="text-white text-sm font-medium">{col}</span><span className="text-gray-400 text-xs">Mean: {typeof mean === 'number' ? mean.toFixed(2) : 'N/A'}</span></div>
                            <div className="relative w-full bg-gray-600 rounded-full h-3">
                              <div className="absolute left-0 top-0 h-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full" style={{ width: `${Math.min(pct, 100)}%` }}></div>
                            </div>
                            <div className="flex justify-between text-xs text-gray-500 mt-1"><span>Min: {typeof min === 'number' ? min.toFixed(2) : min}</span><span>Max: {typeof max === 'number' ? max.toFixed(2) : max}</span></div>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              )}
              {/* Sample Data */}
              {fileDetails.sample_data?.length > 0 && (
                <Card className="bg-gray-800 border-gray-700">
                  <CardHeader><CardTitle className="text-white text-lg">Sample Data</CardTitle></CardHeader>
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
              <Button className="w-full bg-gradient-to-r from-purple-600 to-pink-600" onClick={() => downloadComprehensiveReport({ files, fileDetails }, 'excel')}><Download className="w-4 h-4 mr-2" /> Download Report</Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default WorkspaceView;
