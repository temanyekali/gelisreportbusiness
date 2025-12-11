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
      <div className="flex items-center justify-center h-96">
        <Card className="p-8 text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Akses Ditolak</h2>
          <p className="text-slate-600">Hanya Owner yang dapat mengakses Activity Logs</p>
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
    
    if (filters.user_id !== 'all') {
      filtered = filtered.filter(log => log.user_id === filters.user_id);
    }
    
    if (filters.action !== 'all') {
      filtered = filtered.filter(log => log.action === filters.action);
    }
    
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(log => 
        log.description.toLowerCase().includes(searchLower) ||
        log.action.toLowerCase().includes(searchLower)
      );
    }
    
    if (filters.start_date && filters.end_date) {
      filtered = filtered.filter(log => {
        const logDate = new Date(log.created_at).toISOString().split('T')[0];
        return logDate >= filters.start_date && logDate <= filters.end_date;
      });
    }
    
    setFilteredLogs(filtered);
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
      minute: '2-digit'
    });
  };

  const exportToCSV = () => {
    const headers = ['Timestamp', 'User', 'Action', 'Description'];
    const rows = filteredLogs.map(log => [
      formatDate(log.created_at),
      getUserName(log.user_id),
      log.action,
      log.description
    ]);
    
    const csv = [headers, ...rows].map(row => row.join(',')).join('\\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `activity-logs-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    toast.success('Logs exported!');
  };

  const uniqueActions = [...new Set(logs.map(log => log.action))].sort();

  const stats = {
    total: filteredLogs.length,
    today: filteredLogs.filter(log => {
      const logDate = new Date(log.created_at).toISOString().split('T')[0];
      const today = new Date().toISOString().split('T')[0];
      return logDate === today;
    }).length
  };

  if (loading) {
    return <div className="flex items-center justify-center h-96">Memuat data...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Activity Logs</h1>
          <p className="text-slate-600">Monitor semua aktivitas pengguna</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={fetchData}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button onClick={exportToCSV}>
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="p-4">
          <div className="text-sm text-slate-500">Total Activities</div>
          <div className="text-3xl font-bold text-slate-900 mt-1">{stats.total}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-slate-500">Today</div>
          <div className="text-3xl font-bold text-blue-600 mt-1">{stats.today}</div>
        </Card>
      </div>

      <Card className="p-4">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-5 h-5" />
          <h3 className="font-semibold">Filters</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <Label>User</Label>
            <Select value={filters.user_id} onValueChange={(val) => setFilters({...filters, user_id: val})}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Users</SelectItem>
                {users.map(user => (
                  <SelectItem key={user.id} value={user.id}>{user.full_name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <Label>Action</Label>
            <Select value={filters.action} onValueChange={(val) => setFilters({...filters, action: val})}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Actions</SelectItem>
                {uniqueActions.map(action => (
                  <SelectItem key={action} value={action}>{action}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <Label>Start Date</Label>
            <Input
              type="date"
              value={filters.start_date}
              onChange={(e) => setFilters({...filters, start_date: e.target.value})}
            />
          </div>
          
          <div>
            <Label>Search</Label>
            <Input
              value={filters.search}
              onChange={(e) => setFilters({...filters, search: e.target.value})}
              placeholder="Search..."
            />
          </div>
        </div>
      </Card>

      <Card className="p-6">
        {filteredLogs.length === 0 ? (
          <div className="text-center py-12">
            <Activity className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-600">No activity logs found</p>
          </div>
        ) : (
          <div className="space-y-2">
            {filteredLogs.map((log) => (
              <div key={log.id} className="p-4 border rounded-lg hover:bg-slate-50">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-slate-900">
                    {getUserName(log.user_id)}
                  </span>
                  <span className="text-xs text-slate-500">{formatDate(log.created_at)}</span>
                </div>
                <p className="text-sm text-slate-700">{log.description}</p>
                <div className="text-xs text-slate-500 mt-1">
                  Action: {log.action}
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
