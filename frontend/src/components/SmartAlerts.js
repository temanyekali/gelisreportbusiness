import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { AlertTriangle, AlertCircle, Info, CheckCircle, RefreshCw, X, Eye } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Textarea } from './ui/textarea';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;

const SEVERITY_CONFIG = {
  critical: {
    icon: AlertCircle,
    color: 'text-red-600',
    bg: 'bg-red-50',
    border: 'border-red-200',
    badge: 'bg-red-100 text-red-800'
  },
  warning: {
    icon: AlertTriangle,
    color: 'text-yellow-600',
    bg: 'bg-yellow-50',
    border: 'border-yellow-200',
    badge: 'bg-yellow-100 text-yellow-800'
  },
  info: {
    icon: Info,
    color: 'text-blue-600',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    badge: 'bg-blue-100 text-blue-800'
  }
};

export default function SmartAlerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [checking, setChecking] = useState(false);
  const [filter, setFilter] = useState('unresolved'); // all, resolved, unresolved
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [showResolveModal, setShowResolveModal] = useState(false);
  const [resolveNotes, setResolveNotes] = useState('');

  useEffect(() => {
    fetchAlerts();
    // Auto-refresh setiap 60 detik
    const interval = setInterval(fetchAlerts, 60000);
    return () => clearInterval(interval);
  }, [filter]);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const params = {};
      
      if (filter === 'resolved') {
        params.is_resolved = true;
      } else if (filter === 'unresolved') {
        params.is_resolved = false;
      }

      const response = await axios.get(`${BACKEND_URL}/api/alerts`, {
        params,
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setAlerts(response.data.alerts || []);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckAlerts = async () => {
    setChecking(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${BACKEND_URL}/api/alerts/check`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success(`Alert check selesai! ${response.data.alerts_generated} alert baru digenerate`);
      fetchAlerts();
    } catch (error) {
      toast.error('Gagal melakukan alert check: ' + (error.response?.data?.detail || error.message));
    } finally {
      setChecking(false);
    }
  };

  const handleResolveAlert = (alert) => {
    setSelectedAlert(alert);
    setResolveNotes('');
    setShowResolveModal(true);
  };

  const handleSubmitResolve = async () => {
    if (!selectedAlert) return;

    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `${BACKEND_URL}/api/alerts/${selectedAlert.id}/resolve`,
        null,
        {
          params: { notes: resolveNotes },
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      toast.success('Alert berhasil diresolve');
      setShowResolveModal(false);
      fetchAlerts();
    } catch (error) {
      toast.error('Gagal resolve alert: ' + (error.response?.data?.detail || error.message));
    }
  };

  const groupedAlerts = alerts.reduce((acc, alert) => {
    const severity = alert.severity;
    if (!acc[severity]) acc[severity] = [];
    acc[severity].push(alert);
    return acc;
  }, {});

  const unresolvedCount = alerts.filter(a => !a.is_resolved).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">🚨 Smart Alerts Center</h1>
          <p className="text-gray-500 mt-1">Monitor dan kelola alert sistem secara real-time</p>
        </div>
        <div className="flex gap-2">
          <Button 
            onClick={handleCheckAlerts} 
            disabled={checking}
            className="bg-purple-600 hover:bg-purple-700"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${checking ? 'animate-spin' : ''}`} />
            {checking ? 'Checking...' : 'Check Alerts'}
          </Button>
          <Button onClick={fetchAlerts} variant="outline">
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center">
              <AlertCircle className="w-4 h-4 mr-2" />
              Critical
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {groupedAlerts.critical?.length || 0}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-yellow-500 to-yellow-600 text-white">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center">
              <AlertTriangle className="w-4 h-4 mr-2" />
              Warning
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {groupedAlerts.warning?.length || 0}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center">
              <Info className="w-4 h-4 mr-2" />
              Info
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {groupedAlerts.info?.length || 0}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center">
              <CheckCircle className="w-4 h-4 mr-2" />
              Unresolved
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {unresolvedCount}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filter Tabs */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-2">
            <Button
              variant={filter === 'unresolved' ? 'default' : 'outline'}
              onClick={() => setFilter('unresolved')}
            >
              Unresolved ({unresolvedCount})
            </Button>
            <Button
              variant={filter === 'all' ? 'default' : 'outline'}
              onClick={() => setFilter('all')}
            >
              All ({alerts.length})
            </Button>
            <Button
              variant={filter === 'resolved' ? 'default' : 'outline'}
              onClick={() => setFilter('resolved')}
            >
              Resolved ({alerts.filter(a => a.is_resolved).length})
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Alerts List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      ) : alerts.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <CheckCircle className="w-16 h-16 text-green-500 mb-4" />
            <p className="text-lg font-medium">Tidak ada alerts</p>
            <p className="text-sm text-gray-500 mt-1">Semua sistem berjalan normal</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {/* Critical Alerts First */}
          {groupedAlerts.critical && groupedAlerts.critical.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center text-red-600">
                <AlertCircle className="w-5 h-5 mr-2" />
                Critical Alerts ({groupedAlerts.critical.length})
              </h3>
              <div className="space-y-3">
                {groupedAlerts.critical.map(alert => (
                  <AlertCard 
                    key={alert.id} 
                    alert={alert} 
                    onResolve={handleResolveAlert}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Warning Alerts */}
          {groupedAlerts.warning && groupedAlerts.warning.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center text-yellow-600">
                <AlertTriangle className="w-5 h-5 mr-2" />
                Warning Alerts ({groupedAlerts.warning.length})
              </h3>
              <div className="space-y-3">
                {groupedAlerts.warning.map(alert => (
                  <AlertCard 
                    key={alert.id} 
                    alert={alert} 
                    onResolve={handleResolveAlert}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Info Alerts */}
          {groupedAlerts.info && groupedAlerts.info.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center text-blue-600">
                <Info className="w-5 h-5 mr-2" />
                Info Alerts ({groupedAlerts.info.length})
              </h3>
              <div className="space-y-3">
                {groupedAlerts.info.map(alert => (
                  <AlertCard 
                    key={alert.id} 
                    alert={alert} 
                    onResolve={handleResolveAlert}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Resolve Modal */}
      <Dialog open={showResolveModal} onOpenChange={setShowResolveModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Resolve Alert</DialogTitle>
          </DialogHeader>
          
          {selectedAlert && (
            <div className="space-y-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-semibold mb-2">{selectedAlert.title}</h4>
                <p className="text-sm text-gray-600">{selectedAlert.message}</p>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Catatan Penyelesaian
                </label>
                <Textarea
                  value={resolveNotes}
                  onChange={(e) => setResolveNotes(e.target.value)}
                  placeholder="Jelaskan bagaimana alert ini diselesaikan..."
                  rows={4}
                />
              </div>

              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setShowResolveModal(false)}>
                  Batal
                </Button>
                <Button onClick={handleSubmitResolve} className="bg-green-600 hover:bg-green-700">
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Mark as Resolved
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

function AlertCard({ alert, onResolve }) {
  const config = SEVERITY_CONFIG[alert.severity] || SEVERITY_CONFIG.info;
  const Icon = config.icon;

  return (
    <Card className={`${config.bg} ${config.border} border-2`}>
      <CardContent className="pt-6">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-4 flex-1">
            <Icon className={`w-6 h-6 ${config.color} flex-shrink-0 mt-1`} />
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2">
                <h4 className="font-semibold text-lg">{alert.title}</h4>
                <Badge className={config.badge}>{alert.severity}</Badge>
                {alert.is_resolved && (
                  <Badge className="bg-green-100 text-green-800">Resolved</Badge>
                )}
              </div>

              <p className="text-sm text-gray-700 mb-3">{alert.message}</p>

              <div className="flex flex-wrap gap-4 text-xs text-gray-500">
                <span>
                  ⏰ {new Date(alert.triggered_at).toLocaleString('id-ID')}
                </span>
                {alert.threshold_value && (
                  <span>
                    📊 Threshold: {alert.threshold_value}
                  </span>
                )}
                {alert.current_value && (
                  <span>
                    📈 Current: {alert.current_value}
                  </span>
                )}
              </div>

              {alert.is_resolved && alert.resolved_at && (
                <div className="mt-3 p-2 bg-white rounded text-sm">
                  <span className="font-medium">Resolved:</span> {new Date(alert.resolved_at).toLocaleString('id-ID')}
                  {alert.notes && <p className="mt-1 text-gray-600">{alert.notes}</p>}
                </div>
              )}
            </div>
          </div>

          <div className="flex gap-2 flex-shrink-0 ml-4">
            {alert.action_url && (
              <Button size="sm" variant="outline" asChild>
                <a href={alert.action_url}>
                  <Eye className="w-4 h-4 mr-1" />
                  View
                </a>
              </Button>
            )}
            {!alert.is_resolved && (
              <Button
                size="sm"
                onClick={() => onResolve(alert)}
                className="bg-green-600 hover:bg-green-700"
              >
                <CheckCircle className="w-4 h-4 mr-1" />
                Resolve
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
