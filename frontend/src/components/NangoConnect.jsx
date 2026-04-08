import React, { useState, useEffect, useCallback } from 'react';
import Nango from '@nangohq/frontend';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Loader2, Plug, Unplug, RefreshCw } from 'lucide-react';
import { toast } from '../hooks/use-toast';
import api from '../services/api';

// Supported integrations with display info
const INTEGRATIONS = [
  { id: 'google-ads', name: 'Google Ads', icon: '📊', description: 'Import campaigns & ad performance data' },
  { id: 'google-analytics', name: 'Google Analytics', icon: '📈', description: 'Connect website analytics data' },
  { id: 'google-sheets', name: 'Google Sheets', icon: '📋', description: 'Import data from spreadsheets' },
  { id: 'facebook-ads', name: 'Meta Ads', icon: '📱', description: 'Import ad campaigns & insights' },
];

const NangoConnect = () => {
  const [connections, setConnections] = useState({});
  const [loading, setLoading] = useState(true);
  const [connectingId, setConnectingId] = useState(null);

  const fetchConnections = useCallback(async () => {
    try {
      const res = await api.get('/nango/connections');
      const map = {};
      (res.data.connections || []).forEach(c => {
        map[c.integration_id] = c;
      });
      setConnections(map);
    } catch { /* ignore */ }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchConnections(); }, [fetchConnections]);

  const handleConnect = async (integrationId) => {
    setConnectingId(integrationId);
    try {
      // 1. Get a connect session token from our backend
      const sessionRes = await api.post('/nango/connect-session', {
        allowed_integrations: [integrationId],
      });
      const token = sessionRes.data?.data?.token || sessionRes.data?.token;
      if (!token) throw new Error('Failed to get session token');

      // 2. Use Nango frontend SDK to open OAuth popup
      const nango = new Nango({ connectSessionToken: token });
      const result = await nango.auth(integrationId);

      // 3. Save the connection ID in our backend
      const connectionId = result.connectionId || result.connection_id || `${integrationId}-conn`;
      await api.post('/nango/save-connection', {
        integration_id: integrationId,
        connection_id: connectionId,
      });

      toast({ title: 'Connected!', description: `${integrationId} connected successfully.` });
      fetchConnections();
    } catch (err) {
      if (err?.type === 'authorization_cancelled') {
        toast({ title: 'Cancelled', description: 'Authorization was cancelled.', variant: 'destructive' });
      } else {
        const detail = err?.response?.data?.detail || err?.message || 'Failed to connect.';
        toast({ title: 'Connection Failed', description: detail, variant: 'destructive' });
      }
    } finally { setConnectingId(null); }
  };

  const handleDisconnect = async (integrationId) => {
    try {
      await api.delete(`/nango/connections/${integrationId}`);
      const updated = { ...connections };
      delete updated[integrationId];
      setConnections(updated);
      toast({ title: 'Disconnected', description: `${integrationId} disconnected.` });
    } catch {
      toast({ title: 'Error', description: 'Failed to disconnect.', variant: 'destructive' });
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-purple-400" /></div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-2">
        <p className="text-gray-400 text-sm">Connect your accounts via Nango to import data securely.</p>
        <Button variant="ghost" size="sm" onClick={fetchConnections} className="text-gray-500 hover:text-white">
          <RefreshCw className="w-4 h-4" />
        </Button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {INTEGRATIONS.map((integration) => {
          const conn = connections[integration.id];
          const isConnected = !!conn;
          const isConnecting = connectingId === integration.id;

          return (
            <div
              key={integration.id}
              className={`bg-gray-800/50 border rounded-xl p-5 flex items-center justify-between transition-all ${
                isConnected ? 'border-green-700/50 bg-green-900/10' : 'border-gray-700/50 hover:border-purple-700/50'
              }`}
              data-testid={`nango-integration-${integration.id}`}
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">{integration.icon}</span>
                <div>
                  <h3 className="text-white font-medium text-sm">{integration.name}</h3>
                  <p className="text-gray-500 text-xs">{integration.description}</p>
                  {isConnected && conn.connected_at && (
                    <p className="text-green-500 text-[10px] mt-0.5">Connected {new Date(conn.connected_at).toLocaleDateString()}</p>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2">
                {isConnected && <Badge className="bg-green-900/30 text-green-400 border-green-700 text-[10px]">Active</Badge>}
                {isConnected ? (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleDisconnect(integration.id)}
                    className="border-red-700 text-red-400 hover:bg-red-900/20 text-xs h-8"
                    data-testid={`nango-disconnect-${integration.id}`}
                  >
                    <Unplug className="w-3 h-3 mr-1" /> Disconnect
                  </Button>
                ) : (
                  <Button
                    size="sm"
                    onClick={() => handleConnect(integration.id)}
                    disabled={isConnecting}
                    className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-xs h-8"
                    data-testid={`nango-connect-${integration.id}`}
                  >
                    {isConnecting ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <Plug className="w-3 h-3 mr-1" />}
                    Connect
                  </Button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default NangoConnect;
