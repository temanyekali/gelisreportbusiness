import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';
import { getUser } from '../utils/auth';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { 
  Activity, Filter, Search, Download, RefreshCw,
  User, ShoppingCart, DollarSign, FileText, Users,
  LogIn, LogOut, Edit, Trash2, Plus, CheckCircle,
  AlertCircle, Info, Clock
} from 'lucide-react';
import { toast } from 'sonner';

export default function ActivityLogs() {
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    user_id: 'all',
    action: 'all',
    search: '',
    start_date: new Date(Date.now() - 7*24*60*60*1000).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0]
  });
  
  const currentUser = getUser();
  
  // Only Owner can access
  if (currentUser?.role_id !== 1) {
    return (
      <div className=\"flex items-center justify-center h-96\">
        <Card className=\"p-8 text-center\">
          <AlertCircle className=\"w-16 h-16 text-red-500 mx-auto mb-4\" />
          <h2 className=\"text-2xl font-bold text-slate-900 mb-2\">Akses Ditolak</h2>
          <p className=\"text-slate-600\">Hanya Owner yang dapat mengakses Activity Logs</p>
        </Card>
      </div>
    );
  }

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [filters, logs]);

  const fetchData = async () => {
    try {
      const [logsRes, usersRes] = await Promise.all([
        api.get('/activity-logs'),
        api.get('/users')
      ]);
      setLogs(logsRes.data);
      setUsers(usersRes.data);
    } catch (error) {
      toast.error('Gagal memuat activity logs');
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...logs];
    
    // Filter by user
    if (filters.user_id !== 'all') {
      filtered = filtered.filter(log => log.user_id === filters.user_id);
    }
    
    // Filter by action
    if (filters.action !== 'all') {
      filtered = filtered.filter(log => log.action === filters.action);
    }
    
    // Filter by search
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(log => 
        log.description.toLowerCase().includes(searchLower) ||
        log.action.toLowerCase().includes(searchLower)
      );
    }
    
    // Filter by date range
    if (filters.start_date && filters.end_date) {
      filtered = filtered.filter(log => {
        const logDate = new Date(log.created_at).toISOString().split('T')[0];
        return logDate >= filters.start_date && logDate <= filters.end_date;
      });
    }
    
    setFilteredLogs(filtered);
  };

  const getActionIcon = (action) => {
    const iconMap = {
      'login': LogIn,
      'logout': LogOut,
      'create_order': Plus,
      'update_order': Edit,
      'delete_order': Trash2,
      'create_transaction': DollarSign,
      'update_transaction': Edit,
      'delete_transaction': Trash2,
      'create_user': Users,
      'update_user': Edit,
      'delete_user': Trash2,
      'create_loket_report': FileText,
      'create_kasir_report': FileText,
      'update_loket_report': Edit,
      'update_kasir_report': Edit,
      'delete_loket_report': Trash2,
      'delete_kasir_report': Trash2,
      'teknisi_update_status': CheckCircle,
      'teknisi_update_progress': Activity
    };
    
    const Icon = iconMap[action] || Activity;
    return Icon;
  };

  const getActionBadge = (action) => {
    if (action.includes('login') || action.includes('create')) {
      return <Badge className=\"bg-green-100 text-green-800\">Create/Login</Badge>;
    }
    if (action.includes('update') || action.includes('edit')) {
      return <Badge className=\"bg-blue-100 text-blue-800\">Update</Badge>;
    }
    if (action.includes('delete')) {
      return <Badge className=\"bg-red-100 text-red-800\">Delete</Badge>;
    }
    return <Badge className=\"bg-slate-100 text-slate-800\">Other</Badge>;
  };

  const getUserName = (userId) => {
    const user = users.find(u => u.id === userId);
    return user ? `${user.full_name} (@${user.username})` : 'Unknown User';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('id-ID', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const exportToCSV = () => {
    const headers = ['Timestamp', 'User', 'Action', 'Description', 'IP Address'];
    const rows = filteredLogs.map(log => [
      formatDate(log.created_at),
      getUserName(log.user_id),
      log.action,
      log.description,
      log.ip_address || 'N/A'
    ]);
    
    const csv = [headers, ...rows].map(row => row.join(',')).join('\\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `activity-logs-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    toast.success('Activity logs exported!');
  };

  // Get unique actions
  const uniqueActions = [...new Set(logs.map(log => log.action))].sort();

  // Statistics
  const stats = {
    total: filteredLogs.length,
    today: filteredLogs.filter(log => {
      const logDate = new Date(log.created_at).toISOString().split('T')[0];
      const today = new Date().toISOString().split('T')[0];
      return logDate === today;
    }).length,
    creates: filteredLogs.filter(log => log.action.includes('create') || log.action === 'login').length,
    updates: filteredLogs.filter(log => log.action.includes('update')).length,
    deletes: filteredLogs.filter(log => log.action.includes('delete')).length
  };

  if (loading) {
    return <div className=\"flex items-center justify-center h-96\">Memuat activity logs...</div>;
  }

  return (
    <div className=\"space-y-6\">
      {/* Header */}
      <div className=\"flex items-center justify-between\">
        <div>
          <h1 className=\"text-4xl font-bold text-slate-900 tracking-tight mb-2\">Activity Logs</h1>
          <p className=\"text-slate-600\">Monitor semua aktivitas pengguna di sistem</p>
        </div>
        <div className=\"flex gap-2\">
          <Button variant=\"outline\" onClick={fetchData}>
            <RefreshCw className=\"w-4 h-4 mr-2\" />
            Refresh
          </Button>
          <Button onClick={exportToCSV}>
            <Download className=\"w-4 h-4 mr-2\" />
            Export CSV
          </Button>
        </div>
      </div>

      {/* Statistics */}
      <div className=\"grid grid-cols-1 md:grid-cols-5 gap-4\">
        <Card className=\"p-4\">
          <div className=\"text-sm text-slate-500\">Total Activities</div>
          <div className=\"text-3xl font-bold text-slate-900 mt-1\">{stats.total}</div>
        </Card>
        <Card className=\"p-4\">
          <div className=\"text-sm text-slate-500\">Today</div>
          <div className=\"text-3xl font-bold text-blue-600 mt-1\">{stats.today}</div>
        </Card>
        <Card className=\"p-4\">
          <div className=\"text-sm text-slate-500\">Creates/Logins</div>
          <div className=\"text-3xl font-bold text-green-600 mt-1\">{stats.creates}</div>
        </Card>
        <Card className=\"p-4\">
          <div className=\"text-sm text-slate-500\">Updates</div>
          <div className=\"text-3xl font-bold text-blue-600 mt-1\">{stats.updates}</div>
        </Card>
        <Card className=\"p-4\">
          <div className=\"text-sm text-slate-500\">Deletes</div>
          <div className=\"text-3xl font-bold text-red-600 mt-1\">{stats.deletes}</div>
        </Card>
      </div>

      {/* Filters */}
      <Card className=\"p-4\">
        <div className=\"flex items-center gap-2 mb-4\">
          <Filter className=\"w-5 h-5 text-slate-600\" />
          <h3 className=\"font-semibold text-slate-900\">Filters</h3>
        </div>
        
        <div className=\"grid grid-cols-1 md:grid-cols-5 gap-4\">
          <div>
            <Label>User</Label>
            <Select value={filters.user_id} onValueChange={(val) => setFilters({...filters, user_id: val})}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value=\"all\">All Users</SelectItem>
                {users.map(user => (
                  <SelectItem key={user.id} value={user.id}>
                    {user.full_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <Label>Action Type</Label>
            <Select value={filters.action} onValueChange={(val) => setFilters({...filters, action: val})}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value=\"all\">All Actions</SelectItem>
                {uniqueActions.map(action => (
                  <SelectItem key={action} value={action}>
                    {action.replace(/_/g, ' ').toUpperCase()}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <Label>Start Date</Label>
            <Input
              type=\"date\"
              value={filters.start_date}
              onChange={(e) => setFilters({...filters, start_date: e.target.value})}
            />
          </div>
          
          <div>
            <Label>End Date</Label>
            <Input
              type=\"date\"
              value={filters.end_date}
              onChange={(e) => setFilters({...filters, end_date: e.target.value})}
            />
          </div>
          
          <div>
            <Label>Search</Label>
            <div className=\"relative\">
              <Search className=\"absolute left-3 top-3 w-4 h-4 text-slate-400\" />
              <Input
                value={filters.search}
                onChange={(e) => setFilters({...filters, search: e.target.value})}
                placeholder=\"Search activities...\"
                className=\"pl-10\"
              />
            </div>
          </div>
        </div>
      </Card>

      {/* Activity Logs List */}
      <Card className=\"p-6\">
        <div className=\"space-y-4\">
          {filteredLogs.length === 0 ? (
            <div className=\"text-center py-12\">
              <Activity className=\"w-16 h-16 text-slate-300 mx-auto mb-4\" />
              <h3 className=\"text-lg font-semibold text-slate-900 mb-2\">No Activity Logs</h3>
              <p className=\"text-slate-600\">Tidak ada aktivitas yang sesuai dengan filter</p>
            </div>
          ) : (
            <div className=\"space-y-2\">
              {filteredLogs.map((log) => {
                const Icon = getActionIcon(log.action);
                const user = users.find(u => u.id === log.user_id);
                
                return (
                  <div 
                    key={log.id} 
                    className=\"flex items-start gap-4 p-4 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors\"
                  >
                    {/* Icon */}
                    <div className=\"flex-shrink-0 w-10 h-10 bg-slate-100 rounded-full flex items-center justify-center\">
                      <Icon className=\"w-5 h-5 text-slate-600\" />
                    </div>
                    
                    {/* Content */}
                    <div className=\"flex-1 min-w-0\">
                      <div className=\"flex items-center gap-2 mb-1\">
                        <span className=\"font-semibold text-slate-900\">
                          {user?.full_name || 'Unknown User'}
                        </span>
                        {getActionBadge(log.action)}
                        <span className=\"text-xs text-slate-500\">
                          {formatDate(log.created_at)}
                        </span>
                      </div>
                      
                      <p className=\"text-sm text-slate-700 mb-2\">{log.description}</p>
                      
                      {/* Metadata */}
                      <div className=\"flex items-center gap-4 text-xs text-slate-500\">
                        <span className=\"flex items-center gap-1\">
                          <User className=\"w-3 h-3\" />
                          @{user?.username || 'unknown'}
                        </span>
                        {log.ip_address && (
                          <span className=\"flex items-center gap-1\">
                            <Info className=\"w-3 h-3\" />
                            {log.ip_address}
                          </span>
                        )}
                        {log.related_type && (
                          <span className=\"flex items-center gap-1\">
                            <Activity className=\"w-3 h-3\" />
                            {log.related_type}: {log.related_id?.substring(0, 8)}...
                          </span>
                        )}
                      </div>
                      
                      {/* Metadata Details */}
                      {log.metadata && Object.keys(log.metadata).length > 0 && (
                        <div className=\"mt-2 p-2 bg-slate-50 rounded text-xs\">
                          <span className=\"font-semibold\">Details: </span>
                          {Object.entries(log.metadata).map(([key, value]) => (
                            <span key={key} className=\"mr-3\">
                              {key}: <span className=\"font-mono\">{JSON.stringify(value)}</span>
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
