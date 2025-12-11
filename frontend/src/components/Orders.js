import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { ShoppingCart, Plus, Search, Clock, CheckCircle2, AlertCircle, XCircle, DollarSign, User } from 'lucide-react';
import { toast } from 'sonner';

const ORDER_STATUSES = [
  { value: 'pending', label: 'Pending', color: 'bg-yellow-100 text-yellow-900', icon: Clock },
  { value: 'processing', label: 'Processing', color: 'bg-blue-100 text-blue-900', icon: Clock },
  { value: 'completed', label: 'Completed', color: 'bg-green-100 text-green-900', icon: CheckCircle2 },
  { value: 'cancelled', label: 'Cancelled', color: 'bg-red-100 text-red-900', icon: XCircle },
];

const PAYMENT_STATUSES = [
  { value: 'unpaid', label: 'Belum Bayar', color: 'bg-red-100 text-red-900' },
  { value: 'partial', label: 'DP', color: 'bg-orange-100 text-orange-900' },
  { value: 'paid', label: 'Lunas', color: 'bg-green-100 text-green-900' },
];

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [filteredOrders, setFilteredOrders] = useState([]);
  const [businesses, setBusinesses] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showUpdateDialog, setShowUpdateDialog] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [formData, setFormData] = useState({
    business_id: '',
    customer_name: '',
    customer_phone: '',
    customer_email: '',
    service_type: '',
    total_amount: 0,
    paid_amount: 0,
    payment_method: 'Cash',
    notes: '',
    requires_technician: false,
  });
  const [updateData, setUpdateData] = useState({
    status: '',
    payment_status: '',
    assigned_to: '',
    paid_amount: 0
  });

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    filterOrders();
  }, [orders, searchTerm, statusFilter]);

  const fetchData = async () => {
    try {
      const [ordersRes, businessesRes, usersRes] = await Promise.all([
        api.get('/orders'),
        api.get('/businesses'),
        api.get('/users').catch(() => ({ data: [] }))
      ]);
      setOrders(ordersRes.data);
      setBusinesses(businessesRes.data);
      setUsers(usersRes.data);
    } catch (error) {
      toast.error('Gagal memuat data');
    } finally {
      setLoading(false);
    }
  };

  const filterOrders = () => {
    let filtered = orders;

    if (searchTerm) {
      filtered = filtered.filter(order =>
        order.order_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
        order.customer_name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(order => order.status === statusFilter);
    }

    setFilteredOrders(filtered);
  };

  const handleCreateOrder = async (e) => {
    e.preventDefault();
    try {
      await api.post('/orders', formData);
      toast.success('Pesanan berhasil dibuat!');
      setShowCreateDialog(false);
      resetForm();
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Gagal membuat pesanan');
    }
  };

  const handleUpdateOrder = async (e) => {
    e.preventDefault();
    try {
      const params = new URLSearchParams();
      if (updateData.status) params.append('status', updateData.status);
      if (updateData.payment_status) params.append('payment_status', updateData.payment_status);
      if (updateData.assigned_to) params.append('assigned_to', updateData.assigned_to);
      if (updateData.paid_amount > 0) params.append('paid_amount', updateData.paid_amount);

      await api.put(`/orders/${selectedOrder.id}?${params.toString()}`);
      toast.success('Pesanan berhasil diupdate!');
      setShowUpdateDialog(false);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Gagal update pesanan');
    }
  };

  const resetForm = () => {
    setFormData({
      business_id: '',
      customer_name: '',
      customer_phone: '',
      customer_email: '',
      service_type: '',
      total_amount: 0,
      paid_amount: 0,
      payment_method: 'Cash',
      notes: '',
    });
  };

  const openUpdateDialog = (order) => {
    setSelectedOrder(order);
    setUpdateData({
      status: order.status,
      payment_status: order.payment_status,
      assigned_to: order.assigned_to || '',
      paid_amount: order.paid_amount
    });
    setShowUpdateDialog(true);
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const getStatusBadge = (status) => {
    const statusObj = ORDER_STATUSES.find(s => s.value === status);
    return statusObj || ORDER_STATUSES[0];
  };

  const getPaymentBadge = (paymentStatus) => {
    const statusObj = PAYMENT_STATUSES.find(s => s.value === paymentStatus);
    return statusObj || PAYMENT_STATUSES[0];
  };

  if (loading) {
    return <div className="flex items-center justify-center h-96">Memuat data...</div>;
  }

  const stats = {
    total: orders.length,
    pending: orders.filter(o => o.status === 'pending').length,
    processing: orders.filter(o => o.status === 'processing').length,
    completed: orders.filter(o => o.status === 'completed').length,
    totalRevenue: orders.reduce((sum, o) => sum + (o.paid_amount || 0), 0)
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 tracking-tight mb-2">Manajemen Pesanan</h1>
          <p className="text-slate-600">Kelola pesanan dari semua bisnis</p>
        </div>
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button data-testid="add-order-button">
              <Plus className="w-4 h-4 mr-2" />
              Buat Pesanan
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Buat Pesanan Baru</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreateOrder} className="space-y-4">
              <div>
                <Label>Bisnis *</Label>
                <Select value={formData.business_id} onValueChange={(value) => setFormData({ ...formData, business_id: value })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Pilih bisnis" />
                  </SelectTrigger>
                  <SelectContent>
                    {businesses.map(biz => (
                      <SelectItem key={biz.id} value={biz.id}>{biz.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Nama Customer *</Label>
                  <Input
                    value={formData.customer_name}
                    onChange={(e) => setFormData({ ...formData, customer_name: e.target.value })}
                    required
                    placeholder="Nama lengkap"
                  />
                </div>
                <div>
                  <Label>No. Telepon</Label>
                  <Input
                    value={formData.customer_phone}
                    onChange={(e) => setFormData({ ...formData, customer_phone: e.target.value })}
                    placeholder="081234567890"
                  />
                </div>
              </div>
              <div>
                <Label>Email</Label>
                <Input
                  type="email"
                  value={formData.customer_email}
                  onChange={(e) => setFormData({ ...formData, customer_email: e.target.value })}
                  placeholder="customer@example.com"
                />
              </div>
              <div>
                <Label>Jenis Layanan *</Label>
                <Input
                  value={formData.service_type}
                  onChange={(e) => setFormData({ ...formData, service_type: e.target.value })}
                  required
                  placeholder="Contoh: Instalasi PLN 2200VA"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Total Amount *</Label>
                  <Input
                    type="number"
                    value={formData.total_amount}
                    onChange={(e) => setFormData({ ...formData, total_amount: parseFloat(e.target.value) || 0 })}
                    required
                  />
                </div>
                <div>
                  <Label>Dibayar (DP)</Label>
                  <Input
                    type="number"
                    value={formData.paid_amount}
                    onChange={(e) => setFormData({ ...formData, paid_amount: parseFloat(e.target.value) || 0 })}
                  />
                </div>
              </div>
              <div>
                <Label>Metode Pembayaran</Label>
                <Select value={formData.payment_method} onValueChange={(value) => setFormData({ ...formData, payment_method: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Cash">Cash</SelectItem>
                    <SelectItem value="Transfer">Transfer Bank</SelectItem>
                    <SelectItem value="QRIS">QRIS</SelectItem>
                    <SelectItem value="Debit Card">Debit Card</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Catatan</Label>
                <Textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder="Catatan tambahan"
                  rows={2}
                />
              </div>
              <div className="flex justify-end space-x-2">
                <Button type="button" variant="outline" onClick={() => setShowCreateDialog(false)}>
                  Batal
                </Button>
                <Button type="submit">Simpan Pesanan</Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="p-4">
          <div className="text-sm text-slate-500">Total Pesanan</div>
          <div className="text-3xl font-bold text-slate-900 mt-1">{stats.total}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-slate-500">Pending</div>
          <div className="text-3xl font-bold text-yellow-600 mt-1">{stats.pending}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-slate-500">Processing</div>
          <div className="text-3xl font-bold text-blue-600 mt-1">{stats.processing}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-slate-500">Completed</div>
          <div className="text-3xl font-bold text-green-600 mt-1">{stats.completed}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-slate-500">Total Revenue</div>
          <div className="text-2xl font-bold text-slate-900 mt-1">{formatCurrency(stats.totalRevenue)}</div>
        </Card>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                placeholder="Cari nomor pesanan atau customer..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          <div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Semua Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Semua Status</SelectItem>
                {ORDER_STATUSES.map(status => (
                  <SelectItem key={status.value} value={status.value}>{status.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </Card>

      {/* Orders List */}
      <div className="space-y-4">
        {filteredOrders.map((order) => {
          const business = businesses.find(b => b.id === order.business_id);
          const StatusIcon = getStatusBadge(order.status).icon;
          
          return (
            <Card key={order.id} className="p-6 hover:shadow-md transition-shadow" data-testid={`order-card-${order.id}`}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-slate-900">{order.order_number}</h3>
                    <Badge className={getStatusBadge(order.status).color}>
                      <StatusIcon className="w-3 h-3 mr-1" />
                      {getStatusBadge(order.status).label}
                    </Badge>
                    <Badge className={getPaymentBadge(order.payment_status).color}>
                      <DollarSign className="w-3 h-3 mr-1" />
                      {getPaymentBadge(order.payment_status).label}
                    </Badge>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-slate-500">Customer</div>
                      <div className="font-medium">{order.customer_name}</div>
                    </div>
                    <div>
                      <div className="text-slate-500">Bisnis</div>
                      <div className="font-medium">{business?.name || '-'}</div>
                    </div>
                    <div>
                      <div className="text-slate-500">Layanan</div>
                      <div className="font-medium">{order.service_type}</div>
                    </div>
                    <div>
                      <div className="text-slate-500">Total</div>
                      <div className="font-medium">{formatCurrency(order.total_amount)}</div>
                    </div>
                  </div>
                  <div className="mt-2 text-sm text-slate-600">
                    Dibayar: {formatCurrency(order.paid_amount)} • Sisa: {formatCurrency(order.total_amount - order.paid_amount)}
                  </div>
                </div>
                <div>
                  <Button size="sm" onClick={() => openUpdateDialog(order)}>
                    Update
                  </Button>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {filteredOrders.length === 0 && (
        <Card className="p-12 text-center">
          <ShoppingCart className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-slate-900 mb-2">Tidak Ada Pesanan Ditemukan</h3>
          <p className="text-slate-600">Coba ubah filter atau buat pesanan baru</p>
        </Card>
      )}

      {/* Update Dialog */}
      <Dialog open={showUpdateDialog} onOpenChange={setShowUpdateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Update Pesanan</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleUpdateOrder} className="space-y-4">
            <div>
              <Label>Status Pesanan</Label>
              <Select value={updateData.status} onValueChange={(value) => setUpdateData({ ...updateData, status: value })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {ORDER_STATUSES.map(status => (
                    <SelectItem key={status.value} value={status.value}>{status.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Status Pembayaran</Label>
              <Select value={updateData.payment_status} onValueChange={(value) => setUpdateData({ ...updateData, payment_status: value })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {PAYMENT_STATUSES.map(status => (
                    <SelectItem key={status.value} value={status.value}>{status.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Assign ke Teknisi</Label>
              <Select value={updateData.assigned_to} onValueChange={(value) => setUpdateData({ ...updateData, assigned_to: value })}>
                <SelectTrigger>
                  <SelectValue placeholder="Pilih teknisi" />
                </SelectTrigger>
                <SelectContent>
                  {users.filter(u => u.role_id === 7).map(user => (
                    <SelectItem key={user.id} value={user.id}>{user.full_name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Jumlah Dibayar</Label>
              <Input
                type="number"
                value={updateData.paid_amount}
                onChange={(e) => setUpdateData({ ...updateData, paid_amount: parseFloat(e.target.value) || 0 })}
              />
            </div>
            <div className="flex justify-end space-x-2">
              <Button type="button" variant="outline" onClick={() => setShowUpdateDialog(false)}>
                Batal
              </Button>
              <Button type="submit">Update</Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
