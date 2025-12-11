import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';
import { getUser } from '../utils/auth';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { 
  DollarSign, TrendingUp, TrendingDown, Calendar, Filter,
  Plus, Edit, Trash2, Download, ArrowUpCircle, ArrowDownCircle
} from 'lucide-react';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Label } from './ui/label';

export default function Accounting() {
  const [transactions, setTransactions] = useState([]);
  const [businesses, setBusinesses] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTxn, setEditingTxn] = useState(null);
  const [filters, setFilters] = useState({
    business_id: 'all',
    transaction_type: 'all',
    start_date: new Date(Date.now() - 30*24*60*60*1000).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0]
  });
  
  const [formData, setFormData] = useState({
    business_id: '',
    transaction_type: 'income',
    category: '',
    description: '',
    amount: 0,
    payment_method: 'cash',
    reference_number: ''
  });
  
  const currentUser = getUser();
  const canEdit = currentUser && [1, 2, 3, 5].includes(currentUser.role_id);
  const canDelete = currentUser && [1, 3].includes(currentUser.role_id);

  useEffect(() => {
    fetchData();
  }, [filters]);

  const fetchData = async () => {
    try {
      const [businessesRes, transactionsRes, summaryRes] = await Promise.all([
        api.get('/businesses'),
        api.get('/transactions', {
          params: {
            business_id: filters.business_id !== 'all' ? filters.business_id : undefined,
            transaction_type: filters.transaction_type !== 'all' ? filters.transaction_type : undefined,
            start_date: filters.start_date,
            end_date: filters.end_date
          }
        }),
        api.get('/accounting/summary', {
          params: {
            business_id: filters.business_id !== 'all' ? filters.business_id : undefined,
            start_date: filters.start_date,
            end_date: filters.end_date
          }
        })
      ]);
      
      setBusinesses(businessesRes.data);
      setTransactions(transactionsRes.data);
      setSummary(summaryRes.data);
    } catch (error) {
      toast.error('Gagal memuat data');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingTxn) {
        await api.put(`/transactions/${editingTxn.id}`, formData);
        toast.success('Transaksi berhasil diupdate!');
      } else {
        await api.post('/transactions', formData);
        toast.success('Transaksi berhasil ditambahkan!');
      }
      setShowForm(false);
      setEditingTxn(null);
      resetForm();
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Gagal menyimpan transaksi');
    }
  };

  const handleEdit = (txn) => {
    setEditingTxn(txn);
    setFormData({
      business_id: txn.business_id,
      transaction_type: txn.transaction_type,
      category: txn.category,
      description: txn.description,
      amount: txn.amount,
      payment_method: txn.payment_method || 'cash',
      reference_number: txn.reference_number || ''
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Yakin ingin menghapus transaksi ini?')) return;
    
    try {
      await api.delete(`/transactions/${id}`);
      toast.success('Transaksi berhasil dihapus!');
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Gagal menghapus transaksi');
    }
  };

  const resetForm = () => {
    setFormData({
      business_id: '',
      transaction_type: 'income',
      category: '',
      description: '',
      amount: 0,
      payment_method: 'cash',
      reference_number: ''
    });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('id-ID', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getTransactionBadge = (type) => {
    const config = {
      income: { label: 'Debit', color: 'bg-green-100 text-green-800', icon: ArrowUpCircle },
      expense: { label: 'Kredit', color: 'bg-red-100 text-red-800', icon: ArrowDownCircle },
      transfer: { label: 'Transfer', color: 'bg-blue-100 text-blue-800', icon: DollarSign }
    };
    const cfg = config[type] || config.income;
    const Icon = cfg.icon;
    return (
      <Badge className={cfg.color}>
        <Icon className="w-3 h-3 mr-1" />
        {cfg.label}
      </Badge>
    );
  };

  if (loading) {
    return <div className="flex items-center justify-center h-96">Memuat data...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 tracking-tight mb-2">Akunting</h1>
          <p className="text-slate-600">Kelola arus kas masuk dan keluar</p>
        </div>
        {canEdit && (
          <Button onClick={() => setShowForm(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Tambah Transaksi
          </Button>
        )}
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <Label>Bisnis</Label>
            <Select value={filters.business_id} onValueChange={(val) => setFilters({...filters, business_id: val})}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Semua Bisnis</SelectItem>
                {businesses.map(b => (
                  <SelectItem key={b.id} value={b.id}>{b.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>Tipe</Label>
            <Select value={filters.transaction_type} onValueChange={(val) => setFilters({...filters, transaction_type: val})}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Semua</SelectItem>
                <SelectItem value="income">Debit (Masuk)</SelectItem>
                <SelectItem value="expense">Kredit (Keluar)</SelectItem>
                <SelectItem value="transfer">Transfer</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>Tanggal Mulai</Label>
            <Input 
              type="date" 
              value={filters.start_date}
              onChange={(e) => setFilters({...filters, start_date: e.target.value})}
            />
          </div>
          <div>
            <Label>Tanggal Akhir</Label>
            <Input 
              type="date" 
              value={filters.end_date}
              onChange={(e) => setFilters({...filters, end_date: e.target.value})}
            />
          </div>
        </div>
      </Card>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-slate-500">Total Debit</div>
                <div className="text-2xl font-bold text-green-600 mt-1">
                  {formatCurrency(summary.total_income)}
                </div>
              </div>
              <TrendingUp className="w-10 h-10 text-green-400" />
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-slate-500">Total Kredit</div>
                <div className="text-2xl font-bold text-red-600 mt-1">
                  {formatCurrency(summary.total_expense)}
                </div>
              </div>
              <TrendingDown className="w-10 h-10 text-red-400" />
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-slate-500">Saldo</div>
                <div className={`text-2xl font-bold mt-1 ${
                  summary.balance >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {formatCurrency(summary.balance)}
                </div>
              </div>
              <DollarSign className="w-10 h-10 text-blue-400" />
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-slate-500">Total Transaksi</div>
                <div className="text-2xl font-bold text-slate-900 mt-1">
                  {summary.transaction_count}
                </div>
              </div>
              <Calendar className="w-10 h-10 text-slate-400" />
            </div>
          </Card>
        </div>
      )}

      {/* Transactions List */}
      <Card className="p-6">
        <div className="space-y-4">
          {transactions.length === 0 ? (
            <div className="text-center py-12">
              <DollarSign className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Tidak Ada Transaksi</h3>
              <p className="text-slate-600">Belum ada transaksi untuk periode ini</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4">Tanggal</th>
                    <th className="text-left py-3 px-4">Kode</th>
                    <th className="text-left py-3 px-4">Tipe</th>
                    <th className="text-left py-3 px-4">Kategori</th>
                    <th className="text-left py-3 px-4">Deskripsi</th>
                    <th className="text-right py-3 px-4">Jumlah</th>
                    <th className="text-center py-3 px-4">Aksi</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((txn) => {
                    const business = businesses.find(b => b.id === txn.business_id);
                    return (
                      <tr key={txn.id} className="border-b hover:bg-slate-50">
                        <td className="py-3 px-4 text-sm">{formatDate(txn.created_at)}</td>
                        <td className="py-3 px-4 text-sm font-mono">{txn.transaction_code}</td>
                        <td className="py-3 px-4">{getTransactionBadge(txn.transaction_type)}</td>
                        <td className="py-3 px-4 text-sm">{txn.category}</td>
                        <td className="py-3 px-4 text-sm">
                          <div>{txn.description}</div>
                          <div className="text-xs text-slate-500">{business?.name}</div>
                        </td>
                        <td className={`py-3 px-4 text-right font-semibold ${
                          txn.transaction_type === 'income' ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {txn.transaction_type === 'income' ? '+' : '-'}
                          {formatCurrency(txn.amount)}
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex items-center justify-center gap-2">
                            {canEdit && (
                              <Button size="sm" variant="ghost" onClick={() => handleEdit(txn)}>
                                <Edit className="w-4 h-4" />
                              </Button>
                            )}
                            {canDelete && (
                              <Button size="sm" variant="ghost" onClick={() => handleDelete(txn.id)}>
                                <Trash2 className="w-4 h-4 text-red-600" />
                              </Button>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </Card>

      {/* Form Dialog */}
      <Dialog open={showForm} onOpenChange={setShowForm}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{editingTxn ? 'Edit Transaksi' : 'Tambah Transaksi'}</DialogTitle>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Bisnis *</Label>
                <Select 
                  value={formData.business_id} 
                  onValueChange={(val) => setFormData({...formData, business_id: val})}
                  required
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Pilih bisnis" />
                  </SelectTrigger>
                  <SelectContent>
                    {businesses.map(b => (
                      <SelectItem key={b.id} value={b.id}>{b.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label>Tipe Transaksi *</Label>
                <Select 
                  value={formData.transaction_type} 
                  onValueChange={(val) => setFormData({...formData, transaction_type: val})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="income">Debit (Uang Masuk)</SelectItem>
                    <SelectItem value="expense">Kredit (Uang Keluar)</SelectItem>
                    <SelectItem value="transfer">Transfer</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <Label>Kategori *</Label>
              <Input
                value={formData.category}
                onChange={(e) => setFormData({...formData, category: e.target.value})}
                placeholder="Contoh: Penjualan, Belanja, Gaji, dll"
                required
              />
            </div>

            <div>
              <Label>Deskripsi *</Label>
              <Textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                placeholder="Detail transaksi..."
                rows={3}
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Jumlah (Rp) *</Label>
                <Input
                  type="number"
                  value={formData.amount}
                  onChange={(e) => setFormData({...formData, amount: parseFloat(e.target.value)})}
                  min="0"
                  step="1000"
                  required
                />
              </div>
              
              <div>
                <Label>Metode Pembayaran</Label>
                <Select 
                  value={formData.payment_method} 
                  onValueChange={(val) => setFormData({...formData, payment_method: val})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="cash">Cash</SelectItem>
                    <SelectItem value="transfer">Transfer Bank</SelectItem>
                    <SelectItem value="qris">QRIS</SelectItem>
                    <SelectItem value="card">Kartu Debit/Kredit</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <Label>Nomor Referensi</Label>
              <Input
                value={formData.reference_number}
                onChange={(e) => setFormData({...formData, reference_number: e.target.value})}
                placeholder="Opsional: nomor invoice, bukti transfer, dll"
              />
            </div>

            <div className="flex gap-2 pt-4">
              <Button type="submit" className="flex-1">
                {editingTxn ? 'Update' : 'Simpan'}
              </Button>
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => {
                  setShowForm(false);
                  setEditingTxn(null);
                  resetForm();
                }}
              >
                Batal
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}