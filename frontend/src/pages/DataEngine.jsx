import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Textarea } from '../components/ui/textarea';
import { toast } from '../hooks/use-toast';
import { datasourceAPI, metadataAPI, semanticAPI, queryAPI, authAPI } from '../services/api';
import {
  Database, ArrowLeft, Plus, RefreshCw, Trash2, Search, Play, Clock,
  Table2, Columns3, FileText, BookOpen, Zap, Server, CheckCircle,
  XCircle, Loader2, ChevronRight, ChevronDown, BarChart3, Settings,
  Activity, HardDrive, Cpu, Eye, Copy, Download, AlertTriangle
} from 'lucide-react';

/* ────────────────────────────────────────────── */
/*  DATA ENGINE PAGE                              */
/* ────────────────────────────────────────────── */
export default function DataEngine() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('sources');

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (!userData) { navigate('/login'); return; }
    const parsed = JSON.parse(userData);
    if (parsed.role === 'admin') { navigate('/admin'); return; }
    setUser(parsed);
    authAPI.getCurrentUser().then(setUser).catch(() => {});
  }, [navigate]);

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-950 text-white" data-testid="data-engine-page">
      {/* Top Navigation */}
      <nav className="bg-gray-900 border-b border-gray-800 sticky top-0 z-40">
        <div className="max-w-[1440px] mx-auto px-4 sm:px-6 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button onClick={() => navigate('/dashboard')} className="flex items-center space-x-2 text-gray-400 hover:text-white transition" data-testid="back-to-dashboard">
              <ArrowLeft className="w-4 h-4" />
              <span className="text-sm">Dashboard</span>
            </button>
            <div className="h-5 w-px bg-gray-700" />
            <div className="flex items-center space-x-2">
              <Cpu className="w-5 h-5 text-purple-400" />
              <span className="font-semibold text-lg">Data Engine</span>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <Badge variant="outline" className="border-purple-500/50 text-purple-300 text-xs">
              {user.plan}
            </Badge>
            <span className="text-sm text-gray-400">{user.credits} credits</span>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-[1440px] mx-auto px-4 sm:px-6 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-gray-900 border border-gray-800 p-1 rounded-xl h-auto flex-wrap" data-testid="engine-tabs">
            {[
              { value: 'sources', label: 'Data Sources', icon: Server },
              { value: 'metadata', label: 'Metadata', icon: Table2 },
              { value: 'search', label: 'Semantic Search', icon: Search },
              { value: 'query', label: 'Query Engine', icon: Zap },
              { value: 'glossary', label: 'Glossary', icon: BookOpen },
              { value: 'jobs', label: 'Jobs & Cache', icon: Activity },
            ].map(t => (
              <TabsTrigger key={t.value} value={t.value}
                className="data-[state=active]:bg-purple-600 data-[state=active]:text-white text-gray-400 rounded-lg px-4 py-2 text-sm font-medium"
                data-testid={`engine-tab-${t.value}`}>
                <t.icon className="w-4 h-4 mr-1.5" />{t.label}
              </TabsTrigger>
            ))}
          </TabsList>

          <TabsContent value="sources"><SourcesTab /></TabsContent>
          <TabsContent value="metadata"><MetadataTab /></TabsContent>
          <TabsContent value="search"><SearchTab /></TabsContent>
          <TabsContent value="query"><QueryTab /></TabsContent>
          <TabsContent value="glossary"><GlossaryTab /></TabsContent>
          <TabsContent value="jobs"><JobsTab /></TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

/* ────────────────────────────────────────────── */
/*  SOURCES TAB                                   */
/* ────────────────────────────────────────────── */
function SourcesTab() {
  const [datasources, setDatasources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ name: '', db_type: 'postgresql', host: '', port: 5432, database: '', username: '', password: '', ssl: false, description: '' });
  const [connecting, setConnecting] = useState(false);
  const [testing, setTesting] = useState(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    try { const r = await datasourceAPI.list(); setDatasources(r.datasources || []); } catch { toast({ title: 'Error loading datasources', variant: 'destructive' }); }
    setLoading(false);
  }, []);

  useEffect(() => { fetch(); }, [fetch]);

  const handleConnect = async () => {
    setConnecting(true);
    try {
      const r = await datasourceAPI.connect(form);
      toast({ title: 'Connected!', description: `${r.name} (${r.latency_ms}ms)` });
      setShowAdd(false);
      setForm({ name: '', db_type: 'postgresql', host: '', port: 5432, database: '', username: '', password: '', ssl: false, description: '' });
      fetch();
    } catch (e) {
      toast({ title: 'Connection failed', description: e.response?.data?.detail || e.message, variant: 'destructive' });
    }
    setConnecting(false);
  };

  const handleTest = async (id) => {
    setTesting(id);
    try {
      const r = await datasourceAPI.test(id);
      toast({ title: r.success ? 'Connection OK' : 'Failed', description: r.message, variant: r.success ? 'default' : 'destructive' });
      fetch();
    } catch (e) {
      toast({ title: 'Test failed', variant: 'destructive' });
    }
    setTesting(null);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this datasource and all related metadata?')) return;
    try { await datasourceAPI.delete(id); toast({ title: 'Deleted' }); fetch(); } catch { toast({ title: 'Delete failed', variant: 'destructive' }); }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white">External Data Sources</h2>
          <p className="text-sm text-gray-400 mt-1">Connect PostgreSQL or MySQL databases for live analytics</p>
        </div>
        <Button onClick={() => setShowAdd(true)} className="bg-purple-600 hover:bg-purple-700" data-testid="add-datasource-btn">
          <Plus className="w-4 h-4 mr-1.5" />Add Database
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-16"><Loader2 className="w-6 h-6 animate-spin text-purple-400" /></div>
      ) : datasources.length === 0 ? (
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="flex flex-col items-center justify-center py-16 text-center">
            <Database className="w-12 h-12 text-gray-600 mb-4" />
            <h3 className="text-lg font-medium text-gray-300">No databases connected</h3>
            <p className="text-sm text-gray-500 mt-1 max-w-md">Connect a PostgreSQL or MySQL database to start scanning metadata, running queries, and building semantic search.</p>
            <Button onClick={() => setShowAdd(true)} className="mt-4 bg-purple-600 hover:bg-purple-700" data-testid="add-first-datasource-btn">
              <Plus className="w-4 h-4 mr-1.5" />Connect Database
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {datasources.map(ds => (
            <Card key={ds.id} className="bg-gray-900 border-gray-800 hover:border-gray-700 transition" data-testid={`datasource-card-${ds.id}`}>
              <CardContent className="py-4 px-5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${ds.db_type === 'postgresql' ? 'bg-blue-500/10' : 'bg-orange-500/10'}`}>
                      <Database className={`w-5 h-5 ${ds.db_type === 'postgresql' ? 'text-blue-400' : 'text-orange-400'}`} />
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-white">{ds.name}</span>
                        <Badge className={`text-xs ${ds.status === 'connected' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-red-500/10 text-red-400 border-red-500/30'}`}>
                          {ds.status === 'connected' ? <><CheckCircle className="w-3 h-3 mr-1" />Connected</> : <><XCircle className="w-3 h-3 mr-1" />Error</>}
                        </Badge>
                        <Badge variant="outline" className="text-xs text-gray-400 border-gray-700">{ds.db_type.toUpperCase()}</Badge>
                      </div>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {ds.connection?.host}:{ds.connection?.port}/{ds.connection?.database}
                        {ds.scan_status === 'completed' && <span className="ml-2 text-purple-400">Scanned</span>}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button size="sm" variant="ghost" onClick={() => handleTest(ds.id)} disabled={testing === ds.id} className="text-gray-400 hover:text-white" data-testid={`test-ds-${ds.id}`}>
                      {testing === ds.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
                    </Button>
                    <Button size="sm" variant="ghost" onClick={() => handleDelete(ds.id)} className="text-red-400 hover:text-red-300" data-testid={`delete-ds-${ds.id}`}>
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Add Database Dialog */}
      <Dialog open={showAdd} onOpenChange={setShowAdd}>
        <DialogContent className="bg-gray-900 border-gray-800 text-white max-w-lg" data-testid="add-datasource-dialog">
          <DialogHeader>
            <DialogTitle className="text-white">Connect External Database</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 mt-2">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-gray-300">Name</Label>
                <Input value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} placeholder="My Production DB" className="bg-gray-800 border-gray-700 text-white mt-1" data-testid="ds-form-name" />
              </div>
              <div>
                <Label className="text-gray-300">Type</Label>
                <Select value={form.db_type} onValueChange={v => setForm(p => ({ ...p, db_type: v, port: v === 'mysql' ? 3306 : 5432 }))}>
                  <SelectTrigger className="bg-gray-800 border-gray-700 text-white mt-1" data-testid="ds-form-type">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-gray-800 border-gray-700 text-white">
                    <SelectItem value="postgresql">PostgreSQL</SelectItem>
                    <SelectItem value="mysql">MySQL</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="col-span-2">
                <Label className="text-gray-300">Host</Label>
                <Input value={form.host} onChange={e => setForm(p => ({ ...p, host: e.target.value }))} placeholder="db.example.com" className="bg-gray-800 border-gray-700 text-white mt-1" data-testid="ds-form-host" />
              </div>
              <div>
                <Label className="text-gray-300">Port</Label>
                <Input type="number" value={form.port} onChange={e => setForm(p => ({ ...p, port: parseInt(e.target.value) || 5432 }))} className="bg-gray-800 border-gray-700 text-white mt-1" data-testid="ds-form-port" />
              </div>
            </div>
            <div>
              <Label className="text-gray-300">Database</Label>
              <Input value={form.database} onChange={e => setForm(p => ({ ...p, database: e.target.value }))} placeholder="mydb" className="bg-gray-800 border-gray-700 text-white mt-1" data-testid="ds-form-database" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-gray-300">Username</Label>
                <Input value={form.username} onChange={e => setForm(p => ({ ...p, username: e.target.value }))} placeholder="postgres" className="bg-gray-800 border-gray-700 text-white mt-1" data-testid="ds-form-username" />
              </div>
              <div>
                <Label className="text-gray-300">Password</Label>
                <Input type="password" value={form.password} onChange={e => setForm(p => ({ ...p, password: e.target.value }))} className="bg-gray-800 border-gray-700 text-white mt-1" data-testid="ds-form-password" />
              </div>
            </div>
            <div>
              <Label className="text-gray-300">Description (optional)</Label>
              <Input value={form.description} onChange={e => setForm(p => ({ ...p, description: e.target.value }))} placeholder="Production analytics database" className="bg-gray-800 border-gray-700 text-white mt-1" data-testid="ds-form-description" />
            </div>
            <Button onClick={handleConnect} disabled={connecting || !form.name || !form.host || !form.database || !form.username || !form.password}
              className="w-full bg-purple-600 hover:bg-purple-700" data-testid="ds-form-submit">
              {connecting ? <><Loader2 className="w-4 h-4 animate-spin mr-2" />Connecting...</> : <><Database className="w-4 h-4 mr-2" />Connect & Test</>}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

/* ────────────────────────────────────────────── */
/*  METADATA TAB                                  */
/* ────────────────────────────────────────────── */
function MetadataTab() {
  const [datasources, setDatasources] = useState([]);
  const [selectedDs, setSelectedDs] = useState(null);
  const [tables, setTables] = useState([]);
  const [expandedTable, setExpandedTable] = useState(null);
  const [profiles, setProfiles] = useState({});
  const [scanning, setScanning] = useState(false);
  const [profiling, setProfiling] = useState(false);
  const [enriching, setEnriching] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    datasourceAPI.list().then(r => { setDatasources(r.datasources || []); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const loadTables = async (dsId) => {
    setSelectedDs(dsId);
    setTables([]);
    try { const r = await metadataAPI.getTables(dsId); setTables(r.tables || []); } catch { /* no scan yet */ }
  };

  const handleScan = async () => {
    if (!selectedDs) return;
    setScanning(true);
    try {
      const r = await metadataAPI.scan(selectedDs);
      toast({ title: 'Scan complete', description: `${r.metadata?.total_tables || 0} tables found` });
      loadTables(selectedDs);
    } catch (e) { toast({ title: 'Scan failed', description: e.response?.data?.detail || e.message, variant: 'destructive' }); }
    setScanning(false);
  };

  const handleProfile = async () => {
    if (!selectedDs) return;
    setProfiling(true);
    try {
      const r = await metadataAPI.profile(selectedDs);
      toast({ title: 'Profiling complete', description: `${r.count || 0} tables profiled` });
      const profileMap = {};
      (r.profiles || []).forEach(p => { profileMap[`${p.schema}.${p.table}`] = p; });
      setProfiles(profileMap);
    } catch (e) { toast({ title: 'Profile failed', description: e.response?.data?.detail || e.message, variant: 'destructive' }); }
    setProfiling(false);
  };

  const handleEnrich = async () => {
    if (!selectedDs) return;
    setEnriching(true);
    try {
      await metadataAPI.enrich(selectedDs, false);
      toast({ title: 'AI enrichment complete' });
    } catch (e) { toast({ title: 'Enrich failed', description: e.response?.data?.detail || e.message, variant: 'destructive' }); }
    setEnriching(false);
  };

  if (loading) return <div className="flex justify-center py-16"><Loader2 className="w-6 h-6 animate-spin text-purple-400" /></div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white">Metadata Explorer</h2>
          <p className="text-sm text-gray-400 mt-1">Scan, profile, and enrich your database metadata with AI</p>
        </div>
      </div>

      {/* Datasource Selector */}
      <div className="flex items-center space-x-3">
        <Select value={selectedDs || ''} onValueChange={v => loadTables(v)}>
          <SelectTrigger className="bg-gray-800 border-gray-700 text-white w-72" data-testid="metadata-ds-select">
            <SelectValue placeholder="Select a datasource" />
          </SelectTrigger>
          <SelectContent className="bg-gray-800 border-gray-700 text-white">
            {datasources.map(ds => (
              <SelectItem key={ds.id} value={ds.id}>{ds.name} ({ds.db_type})</SelectItem>
            ))}
          </SelectContent>
        </Select>
        {selectedDs && (
          <>
            <Button size="sm" onClick={handleScan} disabled={scanning} className="bg-purple-600 hover:bg-purple-700" data-testid="scan-btn">
              {scanning ? <Loader2 className="w-4 h-4 animate-spin mr-1.5" /> : <RefreshCw className="w-4 h-4 mr-1.5" />}Scan
            </Button>
            <Button size="sm" onClick={handleProfile} disabled={profiling || tables.length === 0} variant="outline" className="border-gray-700 text-gray-300" data-testid="profile-btn">
              {profiling ? <Loader2 className="w-4 h-4 animate-spin mr-1.5" /> : <BarChart3 className="w-4 h-4 mr-1.5" />}Profile
            </Button>
            <Button size="sm" onClick={handleEnrich} disabled={enriching || tables.length === 0} variant="outline" className="border-gray-700 text-gray-300" data-testid="enrich-btn">
              {enriching ? <Loader2 className="w-4 h-4 animate-spin mr-1.5" /> : <Zap className="w-4 h-4 mr-1.5" />}AI Enrich
            </Button>
          </>
        )}
      </div>

      {/* Tables List */}
      {tables.length > 0 ? (
        <div className="space-y-2">
          {tables.map(t => {
            const key = `${t.schema}.${t.table}`;
            const isExpanded = expandedTable === key;
            const profile = profiles[key];
            return (
              <Card key={key} className="bg-gray-900 border-gray-800" data-testid={`table-card-${key}`}>
                <div className="px-4 py-3 flex items-center justify-between cursor-pointer hover:bg-gray-800/50 transition" onClick={() => setExpandedTable(isExpanded ? null : key)}>
                  <div className="flex items-center space-x-3">
                    {isExpanded ? <ChevronDown className="w-4 h-4 text-gray-500" /> : <ChevronRight className="w-4 h-4 text-gray-500" />}
                    <Table2 className="w-4 h-4 text-purple-400" />
                    <span className="font-medium text-white">{t.schema}<span className="text-gray-500">.</span>{t.table}</span>
                    <Badge variant="outline" className="text-xs text-gray-400 border-gray-700">{t.type}</Badge>
                  </div>
                  <div className="flex items-center space-x-3 text-xs text-gray-500">
                    <span><Columns3 className="w-3 h-3 inline mr-1" />{t.column_count} cols</span>
                    <span>~{(t.row_estimate || 0).toLocaleString()} rows</span>
                  </div>
                </div>
                {isExpanded && (
                  <div className="border-t border-gray-800 px-4 py-3">
                    <Table>
                      <TableHeader>
                        <TableRow className="border-gray-800">
                          <TableHead className="text-gray-400">Column</TableHead>
                          <TableHead className="text-gray-400">Type</TableHead>
                          <TableHead className="text-gray-400">Nullable</TableHead>
                          <TableHead className="text-gray-400">Key</TableHead>
                          {profile && <TableHead className="text-gray-400">Distinct</TableHead>}
                          {profile && <TableHead className="text-gray-400">Nulls%</TableHead>}
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {t.columns?.map(col => {
                          const colProfile = profile?.columns?.find(c => c.column_name === col.name);
                          return (
                            <TableRow key={col.name} className="border-gray-800">
                              <TableCell className="text-white font-mono text-sm">{col.name}</TableCell>
                              <TableCell className="text-purple-300 text-sm">{col.data_type}</TableCell>
                              <TableCell>{col.nullable ? <span className="text-yellow-400 text-sm">YES</span> : <span className="text-gray-500 text-sm">NO</span>}</TableCell>
                              <TableCell>{col.is_primary ? <Badge className="bg-amber-500/10 text-amber-400 border-amber-500/30 text-xs">PK</Badge> : ''}</TableCell>
                              {profile && <TableCell className="text-gray-300 text-sm">{colProfile?.distinct_count?.toLocaleString() || '-'}</TableCell>}
                              {profile && <TableCell className="text-gray-300 text-sm">{colProfile?.null_percentage !== undefined ? `${colProfile.null_percentage}%` : '-'}</TableCell>}
                            </TableRow>
                          );
                        })}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      ) : selectedDs ? (
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="flex flex-col items-center py-12 text-center">
            <Table2 className="w-10 h-10 text-gray-600 mb-3" />
            <p className="text-gray-400">No metadata yet. Click <strong>Scan</strong> to discover tables.</p>
          </CardContent>
        </Card>
      ) : (
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="flex flex-col items-center py-12 text-center">
            <Database className="w-10 h-10 text-gray-600 mb-3" />
            <p className="text-gray-400">Select a datasource to browse metadata</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

/* ────────────────────────────────────────────── */
/*  SEMANTIC SEARCH TAB                           */
/* ────────────────────────────────────────────── */
function SearchTab() {
  const [datasources, setDatasources] = useState([]);
  const [selectedDs, setSelectedDs] = useState(null);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [searching, setSearching] = useState(false);

  useEffect(() => { datasourceAPI.list().then(r => setDatasources(r.datasources || [])).catch(() => {}); }, []);

  const handleSearch = async () => {
    if (!selectedDs || !query.trim()) return;
    setSearching(true);
    try {
      const r = await semanticAPI.search(selectedDs, query.trim());
      setResults(r);
    } catch (e) { toast({ title: 'Search failed', description: e.response?.data?.detail || e.message, variant: 'destructive' }); }
    setSearching(false);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-white">Semantic Search</h2>
        <p className="text-sm text-gray-400 mt-1">Search your database metadata using natural language</p>
      </div>

      <Card className="bg-gray-900 border-gray-800">
        <CardContent className="pt-5 space-y-4">
          <div className="flex items-center space-x-3">
            <Select value={selectedDs || ''} onValueChange={setSelectedDs}>
              <SelectTrigger className="bg-gray-800 border-gray-700 text-white w-64" data-testid="search-ds-select">
                <SelectValue placeholder="Select datasource" />
              </SelectTrigger>
              <SelectContent className="bg-gray-800 border-gray-700 text-white">
                {datasources.map(ds => <SelectItem key={ds.id} value={ds.id}>{ds.name}</SelectItem>)}
              </SelectContent>
            </Select>
            <div className="flex-1 relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
              <Input value={query} onChange={e => setQuery(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSearch()}
                placeholder='e.g. "tables with customer revenue data"'
                className="bg-gray-800 border-gray-700 text-white pl-10" data-testid="semantic-search-input" />
            </div>
            <Button onClick={handleSearch} disabled={searching || !selectedDs || !query.trim()} className="bg-purple-600 hover:bg-purple-700" data-testid="semantic-search-btn">
              {searching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
            </Button>
          </div>
        </CardContent>
      </Card>

      {results && (
        <div className="space-y-4">
          {results.ai_interpretation && (
            <Card className="bg-purple-900/20 border-purple-500/30">
              <CardContent className="py-4">
                <div className="flex items-start space-x-3">
                  <Zap className="w-5 h-5 text-purple-400 mt-0.5 shrink-0" />
                  <p className="text-sm text-purple-200">{results.ai_interpretation}</p>
                </div>
              </CardContent>
            </Card>
          )}

          {results.tables?.length > 0 ? results.tables.map((t, i) => (
            <Card key={i} className="bg-gray-900 border-gray-800" data-testid={`search-result-${i}`}>
              <CardContent className="py-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <Table2 className="w-4 h-4 text-purple-400" />
                    <span className="font-medium text-white">{t.schema}.{t.table}</span>
                    {t.score && <Badge className="text-xs bg-purple-500/10 text-purple-300 border-purple-500/30">score: {typeof t.score === 'number' ? t.score.toFixed(1) : t.score}</Badge>}
                  </div>
                </div>
                {t.description && <p className="text-sm text-gray-400 mb-2">{t.description}</p>}
                {t.columns?.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {t.columns.slice(0, 12).map(c => (
                      <Badge key={c} variant="outline" className="text-xs text-gray-400 border-gray-700 font-mono">{c}</Badge>
                    ))}
                    {t.columns.length > 12 && <Badge variant="outline" className="text-xs text-gray-500 border-gray-700">+{t.columns.length - 12}</Badge>}
                  </div>
                )}
              </CardContent>
            </Card>
          )) : (
            <Card className="bg-gray-900 border-gray-800">
              <CardContent className="py-8 text-center text-gray-400">No matching tables found. Try enriching your metadata with AI first.</CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}

/* ────────────────────────────────────────────── */
/*  QUERY ENGINE TAB                              */
/* ────────────────────────────────────────────── */
function QueryTab() {
  const [datasources, setDatasources] = useState([]);
  const [selectedDs, setSelectedDs] = useState(null);
  const [selectedDbType, setSelectedDbType] = useState('postgresql');
  const [question, setQuestion] = useState('');
  const [sql, setSql] = useState('');
  const [explanation, setExplanation] = useState('');
  const [validation, setValidation] = useState(null);
  const [queryResult, setQueryResult] = useState(null);
  const [mode, setMode] = useState('hybrid');
  const [planning, setPlanning] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    datasourceAPI.list().then(r => {
      const dsList = r.datasources || [];
      setDatasources(dsList);
    }).catch(() => {});
    queryAPI.history().then(r => setHistory(r.history || [])).catch(() => {});
  }, []);

  const handlePlan = async () => {
    if (!selectedDs || !question.trim()) return;
    setPlanning(true);
    setQueryResult(null);
    setValidation(null);
    try {
      const r = await queryAPI.plan(selectedDs, question.trim());
      setSql(r.sql);
      setExplanation(r.explanation);
      const v = await queryAPI.validate(r.sql, r.db_type);
      setValidation(v);
    } catch (e) { toast({ title: 'Planning failed', description: e.response?.data?.detail || e.message, variant: 'destructive' }); }
    setPlanning(false);
  };

  const handleExecute = async () => {
    if (!selectedDs || !sql.trim()) return;
    setExecuting(true);
    try {
      const r = await queryAPI.execute(selectedDs, sql.trim(), mode);
      setQueryResult(r);
      queryAPI.history().then(r2 => setHistory(r2.history || [])).catch(() => {});
    } catch (e) { toast({ title: 'Execution failed', description: e.response?.data?.detail || e.message, variant: 'destructive' }); }
    setExecuting(false);
  };

  const handleValidate = async () => {
    const v = await queryAPI.validate(sql.trim(), selectedDbType);
    setValidation(v);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-white">Query Engine</h2>
        <p className="text-sm text-gray-400 mt-1">Ask questions in natural language or write SQL. Execute in Live, Cached, or Hybrid mode.</p>
      </div>

      {/* NL Question */}
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm text-gray-300 font-medium">Natural Language Query</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center space-x-3">
            <Select value={selectedDs || ''} onValueChange={v => {
              setSelectedDs(v);
              const ds = datasources.find(d => d.id === v);
              if (ds) setSelectedDbType(ds.db_type);
            }}>
              <SelectTrigger className="bg-gray-800 border-gray-700 text-white w-64" data-testid="query-ds-select">
                <SelectValue placeholder="Select datasource" />
              </SelectTrigger>
              <SelectContent className="bg-gray-800 border-gray-700 text-white">
                {datasources.map(ds => <SelectItem key={ds.id} value={ds.id}>{ds.name}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={mode} onValueChange={setMode}>
              <SelectTrigger className="bg-gray-800 border-gray-700 text-white w-36" data-testid="query-mode-select">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-gray-800 border-gray-700 text-white">
                <SelectItem value="live">Live</SelectItem>
                <SelectItem value="cached">Cached</SelectItem>
                <SelectItem value="hybrid">Hybrid</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex space-x-3">
            <Input value={question} onChange={e => setQuestion(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handlePlan()}
              placeholder='e.g. "Show me top 10 customers by revenue this month"'
              className="bg-gray-800 border-gray-700 text-white flex-1" data-testid="query-nl-input" />
            <Button onClick={handlePlan} disabled={planning || !selectedDs || !question.trim()} className="bg-purple-600 hover:bg-purple-700" data-testid="query-plan-btn">
              {planning ? <Loader2 className="w-4 h-4 animate-spin mr-1.5" /> : <Zap className="w-4 h-4 mr-1.5" />}Plan
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* SQL Editor */}
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm text-gray-300 font-medium">SQL Query</CardTitle>
            <div className="flex items-center space-x-2">
              <Button size="sm" variant="ghost" onClick={handleValidate} disabled={!sql.trim()} className="text-gray-400 hover:text-white" data-testid="validate-sql-btn">
                <CheckCircle className="w-4 h-4 mr-1" />Validate
              </Button>
              <Button size="sm" onClick={handleExecute} disabled={executing || !selectedDs || !sql.trim()}
                className="bg-emerald-600 hover:bg-emerald-700" data-testid="execute-sql-btn">
                {executing ? <Loader2 className="w-4 h-4 animate-spin mr-1.5" /> : <Play className="w-4 h-4 mr-1.5" />}Execute
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <Textarea value={sql} onChange={e => setSql(e.target.value)} rows={5}
            className="bg-gray-800 border-gray-700 text-white font-mono text-sm" placeholder="SELECT ..." data-testid="sql-editor" />
          {explanation && <p className="text-xs text-purple-300 bg-purple-900/20 p-2 rounded">{explanation}</p>}
          {validation && (
            <div className="space-y-1">
              {validation.valid ? (
                <p className="text-xs text-emerald-400 flex items-center"><CheckCircle className="w-3 h-3 mr-1" />SQL is valid</p>
              ) : validation.issues?.map((issue, i) => (
                <p key={i} className="text-xs text-red-400 flex items-center"><XCircle className="w-3 h-3 mr-1" />{issue}</p>
              ))}
              {validation.warnings?.map((w, i) => (
                <p key={i} className="text-xs text-yellow-400 flex items-center"><AlertTriangle className="w-3 h-3 mr-1" />{w}</p>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Query Results */}
      {queryResult && (
        <Card className="bg-gray-900 border-gray-800" data-testid="query-results">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm text-gray-300 font-medium">
                Results ({queryResult.row_count} rows)
              </CardTitle>
              <div className="flex items-center space-x-3 text-xs text-gray-500">
                <span><Clock className="w-3 h-3 inline mr-1" />{queryResult.execution_time_ms}ms</span>
                <Badge className={`text-xs ${queryResult.source === 'cache' ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'}`}>
                  {queryResult.source}
                </Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto max-h-[400px] overflow-y-auto">
              <Table>
                <TableHeader>
                  <TableRow className="border-gray-800">
                    {queryResult.columns?.map(c => <TableHead key={c} className="text-gray-400 font-mono text-xs whitespace-nowrap">{c}</TableHead>)}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {queryResult.rows?.slice(0, 100).map((row, i) => (
                    <TableRow key={i} className="border-gray-800">
                      {queryResult.columns?.map(c => (
                        <TableCell key={c} className="text-gray-300 text-sm whitespace-nowrap max-w-[200px] truncate">{String(row[c] ?? '')}</TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Query History */}
      {history.length > 0 && (
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-gray-300 font-medium">Recent Queries</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {history.slice(0, 10).map((h, i) => (
                <div key={i} className="flex items-center justify-between text-sm py-2 border-b border-gray-800 last:border-0 cursor-pointer hover:bg-gray-800/50 px-2 rounded"
                  onClick={() => setSql(h.sql)} data-testid={`history-item-${i}`}>
                  <span className="font-mono text-gray-300 truncate max-w-[60%]">{h.sql}</span>
                  <div className="flex items-center space-x-3 text-xs text-gray-500 shrink-0">
                    <span>{h.row_count} rows</span>
                    <span>{h.execution_time_ms}ms</span>
                    <Badge variant="outline" className="text-xs border-gray-700">{h.source}</Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

/* ────────────────────────────────────────────── */
/*  GLOSSARY TAB                                  */
/* ────────────────────────────────────────────── */
function GlossaryTab() {
  const [terms, setTerms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ term: '', definition: '', synonyms: '', related_tables: [], related_columns: [] });
  const [saving, setSaving] = useState(false);
  const [editingId, setEditingId] = useState(null);

  const fetchTerms = useCallback(async () => {
    setLoading(true);
    try { const r = await semanticAPI.listGlossary(search); setTerms(r.terms || []); } catch {}
    setLoading(false);
  }, [search]);

  useEffect(() => { fetchTerms(); }, [fetchTerms]);

  const handleSave = async () => {
    setSaving(true);
    try {
      if (editingId) {
        await semanticAPI.updateGlossaryTerm(editingId, form);
      } else {
        await semanticAPI.createGlossaryTerm(form);
      }
      toast({ title: editingId ? 'Term updated' : 'Term added' });
      setShowAdd(false);
      setForm({ term: '', definition: '', synonyms: '', related_tables: [], related_columns: [] });
      setEditingId(null);
      fetchTerms();
    } catch (e) { toast({ title: 'Save failed', variant: 'destructive' }); }
    setSaving(false);
  };

  const handleEdit = (t) => {
    setEditingId(t.id);
    setForm({ term: t.term, definition: t.definition, synonyms: t.synonyms || '', related_tables: t.related_tables || [], related_columns: t.related_columns || [] });
    setShowAdd(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this glossary term?')) return;
    try { await semanticAPI.deleteGlossaryTerm(id); toast({ title: 'Deleted' }); fetchTerms(); } catch { toast({ title: 'Delete failed', variant: 'destructive' }); }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white">Business Glossary</h2>
          <p className="text-sm text-gray-400 mt-1">Define business terms and map them to database tables/columns</p>
        </div>
        <Button onClick={() => { setEditingId(null); setForm({ term: '', definition: '', synonyms: '', related_tables: [], related_columns: [] }); setShowAdd(true); }}
          className="bg-purple-600 hover:bg-purple-700" data-testid="add-glossary-btn">
          <Plus className="w-4 h-4 mr-1.5" />Add Term
        </Button>
      </div>

      <div className="relative">
        <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
        <Input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search glossary..." className="bg-gray-800 border-gray-700 text-white pl-10" data-testid="glossary-search" />
      </div>

      {loading ? (
        <div className="flex justify-center py-16"><Loader2 className="w-6 h-6 animate-spin text-purple-400" /></div>
      ) : terms.length === 0 ? (
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="flex flex-col items-center py-12 text-center">
            <BookOpen className="w-10 h-10 text-gray-600 mb-3" />
            <p className="text-gray-400">{search ? 'No matching terms' : 'No glossary terms yet. Add one to improve semantic search.'}</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-3">
          {terms.map(t => (
            <Card key={t.id} className="bg-gray-900 border-gray-800" data-testid={`glossary-term-${t.id}`}>
              <CardContent className="py-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-medium text-white">{t.term}</h3>
                    <p className="text-sm text-gray-400 mt-1">{t.definition}</p>
                    {t.synonyms && <p className="text-xs text-gray-500 mt-1">Synonyms: {t.synonyms}</p>}
                    {t.related_tables?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {t.related_tables.map(rt => <Badge key={rt} variant="outline" className="text-xs text-purple-300 border-purple-500/30">{rt}</Badge>)}
                      </div>
                    )}
                  </div>
                  <div className="flex items-center space-x-1 shrink-0">
                    <Button size="sm" variant="ghost" onClick={() => handleEdit(t)} className="text-gray-400 hover:text-white" data-testid={`edit-glossary-${t.id}`}>
                      <FileText className="w-4 h-4" />
                    </Button>
                    <Button size="sm" variant="ghost" onClick={() => handleDelete(t.id)} className="text-red-400 hover:text-red-300" data-testid={`delete-glossary-${t.id}`}>
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Add/Edit Dialog */}
      <Dialog open={showAdd} onOpenChange={v => { setShowAdd(v); if (!v) setEditingId(null); }}>
        <DialogContent className="bg-gray-900 border-gray-800 text-white" data-testid="glossary-dialog">
          <DialogHeader>
            <DialogTitle className="text-white">{editingId ? 'Edit Term' : 'Add Glossary Term'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 mt-2">
            <div>
              <Label className="text-gray-300">Term</Label>
              <Input value={form.term} onChange={e => setForm(p => ({ ...p, term: e.target.value }))} placeholder='e.g. "Monthly Recurring Revenue"' className="bg-gray-800 border-gray-700 text-white mt-1" data-testid="glossary-form-term" />
            </div>
            <div>
              <Label className="text-gray-300">Definition</Label>
              <Textarea value={form.definition} onChange={e => setForm(p => ({ ...p, definition: e.target.value }))} placeholder="Sum of all recurring subscription revenue..." rows={3} className="bg-gray-800 border-gray-700 text-white mt-1" data-testid="glossary-form-definition" />
            </div>
            <div>
              <Label className="text-gray-300">Synonyms (comma-separated)</Label>
              <Input value={form.synonyms} onChange={e => setForm(p => ({ ...p, synonyms: e.target.value }))} placeholder="MRR, recurring revenue" className="bg-gray-800 border-gray-700 text-white mt-1" data-testid="glossary-form-synonyms" />
            </div>
            <Button onClick={handleSave} disabled={saving || !form.term || !form.definition} className="w-full bg-purple-600 hover:bg-purple-700" data-testid="glossary-form-submit">
              {saving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
              {editingId ? 'Update Term' : 'Add Term'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

/* ────────────────────────────────────────────── */
/*  JOBS & CACHE TAB                              */
/* ────────────────────────────────────────────── */
function JobsTab() {
  const [jobs, setJobs] = useState([]);
  const [cacheStats, setCacheStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const [j, c] = await Promise.all([metadataAPI.listJobs(), queryAPI.cacheStats()]);
        setJobs(j.jobs || []);
        setCacheStats(c);
      } catch {}
      setLoading(false);
    };
    load();
    const interval = setInterval(load, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="flex justify-center py-16"><Loader2 className="w-6 h-6 animate-spin text-purple-400" /></div>;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-white">Background Jobs & Cache</h2>
        <p className="text-sm text-gray-400 mt-1">Monitor running tasks and Redis cache status</p>
      </div>

      {/* Cache Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="py-4 flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
              <HardDrive className={`w-5 h-5 ${cacheStats?.connected ? 'text-emerald-400' : 'text-red-400'}`} />
            </div>
            <div>
              <p className="text-xs text-gray-500">Redis</p>
              <p className="font-medium text-white">{cacheStats?.connected ? 'Connected' : 'Disconnected'}</p>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="py-4 flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
              <Activity className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="text-xs text-gray-500">Cached Keys</p>
              <p className="font-medium text-white">{cacheStats?.keys_count ?? 0}</p>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="py-4 flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
              <Cpu className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <p className="text-xs text-gray-500">Memory Used</p>
              <p className="font-medium text-white">{cacheStats?.used_memory || 'N/A'}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Background Jobs */}
      <Card className="bg-gray-900 border-gray-800">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm text-gray-300 font-medium">Background Jobs</CardTitle>
        </CardHeader>
        <CardContent>
          {jobs.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-6">No background jobs have been run yet</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="border-gray-800">
                  <TableHead className="text-gray-400">Job ID</TableHead>
                  <TableHead className="text-gray-400">Type</TableHead>
                  <TableHead className="text-gray-400">Status</TableHead>
                  <TableHead className="text-gray-400">Started</TableHead>
                  <TableHead className="text-gray-400">Completed</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {jobs.map(j => (
                  <TableRow key={j.id} className="border-gray-800" data-testid={`job-row-${j.id}`}>
                    <TableCell className="font-mono text-sm text-gray-300">{j.id}</TableCell>
                    <TableCell><Badge variant="outline" className="text-xs text-gray-400 border-gray-700">{j.type}</Badge></TableCell>
                    <TableCell>
                      <Badge className={`text-xs ${
                        j.status === 'completed' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' :
                        j.status === 'running' ? 'bg-blue-500/10 text-blue-400 border-blue-500/30' :
                        j.status === 'failed' ? 'bg-red-500/10 text-red-400 border-red-500/30' :
                        'bg-gray-500/10 text-gray-400 border-gray-500/30'
                      }`}>
                        {j.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-gray-400">{j.started_at ? new Date(j.started_at).toLocaleString() : '-'}</TableCell>
                    <TableCell className="text-sm text-gray-400">{j.completed_at ? new Date(j.completed_at).toLocaleString() : '-'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
