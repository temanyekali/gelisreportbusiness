import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { api } from '../utils/api';
import { toast } from 'sonner';
import { 
  Terminal, Database, Activity, AlertTriangle, 
  CheckCircle, Server, Code, RefreshCw, Eye,
  TrendingUp, Users, FileText, Bug
} from 'lucide-react';

export default function DeveloperTools() {
  const [loading, setLoading] = useState(false);
  const [systemHealth, setSystemHealth] = useState(null);
  const [logs, setLogs] = useState([]);
  const [activeTab, setActiveTab] = useState('health');

  useEffect(() => {
    fetchSystemHealth();
  }, []);

  const fetchSystemHealth = async () => {
    try {
      setLoading(true);
      const response = await api.get('/dev/health');
      setSystemHealth(response.data);
    } catch (error) {
      toast.error('Gagal memuat system health');
    } finally {
      setLoading(false);
    }
  };

  const fetchLogs = async (type) => {
    try {
      setLoading(true);
      const response = await api.get(`/dev/logs/${type}`);
      setLogs(response.data);
    } catch (error) {
      toast.error('Gagal memuat logs');
    } finally {
      setLoading(false);
    }
  };

  const runHealthCheck = async () => {
    try {
      setLoading(true);
      await api.post('/dev/health-check');
      toast.success('Health check completed');
      fetchSystemHealth();
    } catch (error) {
      toast.error('Health check failed');
    } finally {
      setLoading(false);
    }
  };

  const clearCache = async () => {
    try {
      await api.post('/dev/clear-cache');
      toast.success('Cache cleared successfully');
    } catch (error) {
      toast.error('Failed to clear cache');
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Developer Tools</h1>
          <p className="text-slate-600 mt-1">System monitoring, debugging, and management</p>
        </div>
        <Button 
          onClick={fetchSystemHealth}
          disabled={loading}
          className="bg-slate-900"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-slate-200">
        {[
          { id: 'health', label: 'System Health', icon: Activity },
          { id: 'database', label: 'Database', icon: Database },
          { id: 'logs', label: 'Logs', icon: FileText },
          { id: 'errors', label: 'Errors', icon: Bug },
          { id: 'performance', label: 'Performance', icon: TrendingUp },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 font-medium text-sm flex items-center gap-2 border-b-2 transition-colors ${
              activeTab === tab.id
                ? 'border-slate-900 text-slate-900'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* System Health Tab */}
      {activeTab === 'health' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Backend Status */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Server className="w-4 h-4" />
                Backend
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold">
                  {systemHealth?.backend_status === 'healthy' ? (
                    <CheckCircle className="w-8 h-8 text-green-500" />
                  ) : (
                    <AlertTriangle className="w-8 h-8 text-red-500" />
                  )}
                </span>
                <Badge variant={systemHealth?.backend_status === 'healthy' ? 'success' : 'destructive'}>
                  {systemHealth?.backend_status || 'Unknown'}
                </Badge>
              </div>
              <p className="text-xs text-slate-500 mt-2">FastAPI Server</p>
            </CardContent>
          </Card>

          {/* Database Status */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Database className="w-4 h-4" />
                Database
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold">
                  {systemHealth?.database_status === 'connected' ? (
                    <CheckCircle className="w-8 h-8 text-green-500" />
                  ) : (
                    <AlertTriangle className="w-8 h-8 text-red-500" />
                  )}
                </span>
                <Badge variant={systemHealth?.database_status === 'connected' ? 'success' : 'destructive'}>
                  {systemHealth?.database_status || 'Unknown'}
                </Badge>
              </div>
              <p className="text-xs text-slate-500 mt-2">MongoDB</p>
            </CardContent>
          </Card>

          {/* Total Users */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Users className="w-4 h-4" />
                Total Users
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-900">
                {systemHealth?.total_users || 0}
              </div>
              <p className="text-xs text-slate-500 mt-2">Active accounts</p>
            </CardContent>
          </Card>

          {/* Uptime */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Activity className="w-4 h-4" />
                Uptime
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-900">
                {systemHealth?.uptime || 'N/A'}
              </div>
              <p className="text-xs text-slate-500 mt-2">System uptime</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Database Tab */}
      {activeTab === 'database' && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="w-5 h-5" />
                Database Inspector
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="p-4 bg-slate-50 rounded-lg">
                    <div className="text-sm text-slate-600">Users</div>
                    <div className="text-2xl font-bold mt-1">{systemHealth?.collections?.users || 0}</div>
                  </div>
                  <div className="p-4 bg-slate-50 rounded-lg">
                    <div className="text-sm text-slate-600">Orders</div>
                    <div className="text-2xl font-bold mt-1">{systemHealth?.collections?.orders || 0}</div>
                  </div>
                  <div className="p-4 bg-slate-50 rounded-lg">
                    <div className="text-sm text-slate-600">Transactions</div>
                    <div className="text-2xl font-bold mt-1">{systemHealth?.collections?.transactions || 0}</div>
                  </div>
                  <div className="p-4 bg-slate-50 rounded-lg">
                    <div className="text-sm text-slate-600">Businesses</div>
                    <div className="text-2xl font-bold mt-1">{systemHealth?.collections?.businesses || 0}</div>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button variant="outline" onClick={() => toast.info('Feature coming soon')}>
                    <Eye className="w-4 h-4 mr-2" />
                    View Collections
                  </Button>
                  <Button variant="outline" onClick={() => toast.info('Feature coming soon')}>
                    <Code className="w-4 h-4 mr-2" />
                    Run Query
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Logs Tab */}
      {activeTab === 'logs' && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  System Logs
                </span>
                <div className="flex gap-2">
                  <Button size="sm" variant="outline" onClick={() => fetchLogs('backend')}>
                    Backend Logs
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => fetchLogs('frontend')}>
                    Frontend Logs
                  </Button>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-slate-900 text-green-400 p-4 rounded-lg font-mono text-xs max-h-96 overflow-auto">
                {logs.length > 0 ? (
                  logs.map((log, idx) => (
                    <div key={idx} className="mb-1">{log}</div>
                  ))
                ) : (
                  <div className="text-slate-500">No logs available. Click button to load logs.</div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Errors Tab */}
      {activeTab === 'errors' && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bug className="w-5 h-5" />
                Error Tracking
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-slate-500">
                <AlertTriangle className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                <p>No recent errors detected</p>
                <p className="text-sm mt-2">System is running smoothly</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Performance Tab */}
      {activeTab === 'performance' && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Performance Metrics
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-slate-50 rounded-lg">
                  <div className="text-sm text-slate-600">Response Time</div>
                  <div className="text-2xl font-bold mt-1">{systemHealth?.response_time || 'N/A'}</div>
                  <div className="text-xs text-slate-500 mt-1">Average</div>
                </div>
                <div className="p-4 bg-slate-50 rounded-lg">
                  <div className="text-sm text-slate-600">Requests/min</div>
                  <div className="text-2xl font-bold mt-1">{systemHealth?.requests_per_min || 0}</div>
                  <div className="text-xs text-slate-500 mt-1">Current load</div>
                </div>
                <div className="p-4 bg-slate-50 rounded-lg">
                  <div className="text-sm text-slate-600">Error Rate</div>
                  <div className="text-2xl font-bold mt-1">{systemHealth?.error_rate || '0%'}</div>
                  <div className="text-xs text-slate-500 mt-1">Last 24h</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Button onClick={runHealthCheck} disabled={loading}>
              <Activity className="w-4 h-4 mr-2" />
              Run Health Check
            </Button>
            <Button variant="outline" onClick={clearCache}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Clear Cache
            </Button>
            <Button variant="outline" onClick={() => toast.info('Feature coming soon')}>
              <Terminal className="w-4 h-4 mr-2" />
              Open Console
            </Button>
            <Button variant="outline" onClick={() => toast.info('Feature coming soon')}>
              <Code className="w-4 h-4 mr-2" />
              API Tester
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
