import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';
import { getUser } from '../utils/auth';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  Wrench, MapPin, Clock, CheckCircle, AlertCircle, 
  PlayCircle, Pause, Calendar, Building2, User, TrendingUp 
} from 'lucide-react';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import TechnicalProgressTracker from './TechnicalProgressTracker';

export default function TeknisiDashboard() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [showUpdateModal, setShowUpdateModal] = useState(false);
  const [showProgressModal, setShowProgressModal] = useState(false);
  const [updateData, setUpdateData] = useState({
    status: '',
    progress: 0,
    notes: ''
  });
  const [businesses, setBusinesses] = useState([]);
  
  const currentUser = getUser();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [ordersRes, businessesRes] = await Promise.all([
        api.get('/teknisi/orders'),
        api.get('/businesses')
      ]);
      setOrders(ordersRes.data);
      setBusinesses(businessesRes.data);
    } catch (error) {
      toast.error('Gagal memuat data');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = (order) => {
    setSelectedOrder(order);
    setUpdateData({
      status: order.status,
      progress: order.order_details?.progress || 0,
      notes: ''
    });
    setShowUpdateModal(true);
  };

  const handleSubmitUpdate = async () => {
    if (!selectedOrder) return;
    
    try {
      // Update status
      await api.put(`/teknisi/orders/${selectedOrder.id}/status`, {
        status: updateData.status,
        notes: updateData.notes
      });
      
      // Update progress if changed
      if (updateData.progress !== (selectedOrder.order_details?.progress || 0)) {
        await api.put(`/teknisi/orders/${selectedOrder.id}/progress`, {
          progress: updateData.progress,
          notes: updateData.notes
        });
      }
      
      toast.success('Status berhasil diupdate!');
      setShowUpdateModal(false);
      setSelectedOrder(null);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Gagal update status');
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { label: 'Pending', color: 'bg-yellow-100 text-yellow-800' },
      processing: { label: 'Dalam Proses', color: 'bg-blue-100 text-blue-800' },
      completed: { label: 'Selesai', color: 'bg-green-100 text-green-800' },
      cancelled: { label: 'Dibatalkan', color: 'bg-red-100 text-red-800' }
    };
    
    const config = statusConfig[status] || statusConfig.pending;
    return <Badge className={config.color}>{config.label}</Badge>;
  };

  const getProgressColor = (progress) => {
    if (progress === 0) return 'bg-gray-200';
    if (progress < 50) return 'bg-yellow-400';
    if (progress < 100) return 'bg-blue-500';
    return 'bg-green-500';
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('id-ID', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getPendingOrders = () => orders.filter(o => o.status === 'pending');
  const getProcessingOrders = () => orders.filter(o => o.status === 'processing');
  const getCompletedOrders = () => orders.filter(o => o.status === 'completed');

  if (loading) {
    return <div className="flex items-center justify-center h-96">Memuat data...</div>;
  }

  return (
    <div className="space-y-4 md:space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl md:text-3xl lg:text-4xl font-bold text-slate-900 tracking-tight mb-1 md:mb-2">
            Dashboard Teknisi
          </h1>
          <p className="text-sm md:text-base text-slate-600">
            Halo {currentUser?.full_name}, kelola pekerjaan Anda di sini
          </p>
        </div>
      </div>

      {/* Stats Cards - Scrollable on mobile */}
      <div className="overflow-x-auto -mx-3 md:mx-0 px-3 md:px-0">
        <div className="flex md:grid md:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4 pb-2 md:pb-0" style={{ minWidth: 'max-content' }}>
          <div className="min-w-[200px] md:min-w-0">
            <Card className="p-3 md:p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-xs md:text-sm text-slate-500">Total Pekerjaan</div>
                  <div className="text-2xl md:text-3xl font-bold text-slate-900 mt-1">{orders.length}</div>
                </div>
                <Wrench className="w-8 h-8 md:w-10 md:h-10 text-slate-400" />
              </div>
            </Card>
          </div>
          <div className="min-w-[200px] md:min-w-0">
            <Card className="p-3 md:p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-xs md:text-sm text-slate-500">Pending</div>
                  <div className="text-2xl md:text-3xl font-bold text-yellow-600 mt-1">{getPendingOrders().length}</div>
                </div>
                <AlertCircle className="w-8 h-8 md:w-10 md:h-10 text-yellow-400" />
              </div>
            </Card>
          </div>
          <div className="min-w-[200px] md:min-w-0">
            <Card className="p-3 md:p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-xs md:text-sm text-slate-500">Dalam Proses</div>
                  <div className="text-2xl md:text-3xl font-bold text-blue-600 mt-1">{getProcessingOrders().length}</div>
                </div>
                <PlayCircle className="w-8 h-8 md:w-10 md:h-10 text-blue-400" />
              </div>
            </Card>
          </div>
          <div className="min-w-[200px] md:min-w-0">
            <Card className="p-3 md:p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-xs md:text-sm text-slate-500">Selesai</div>
                  <div className="text-2xl md:text-3xl font-bold text-green-600 mt-1">{getCompletedOrders().length}</div>
                </div>
                <CheckCircle className="w-8 h-8 md:w-10 md:h-10 text-green-400" />
              </div>
            </Card>
          </div>
        </div>
      </div>

      {/* Orders Tabs */}
      <Tabs defaultValue="all" className="w-full">
        <div className="overflow-x-auto -mx-3 md:mx-0">
          <TabsList className="inline-flex md:grid w-full md:grid-cols-4 min-w-max md:min-w-0">
            <TabsTrigger value="all" className="whitespace-nowrap px-3 md:px-4">Semua ({orders.length})</TabsTrigger>
            <TabsTrigger value="pending" className="whitespace-nowrap px-3 md:px-4">Pending ({getPendingOrders().length})</TabsTrigger>
            <TabsTrigger value="processing" className="whitespace-nowrap px-3 md:px-4">Proses ({getProcessingOrders().length})</TabsTrigger>
            <TabsTrigger value="completed" className="whitespace-nowrap px-3 md:px-4">Selesai ({getCompletedOrders().length})</TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="all" className="space-y-3 md:space-y-4 mt-4 md:mt-6">
          {orders.map((order) => {
            const business = businesses.find(b => b.id === order.business_id);
            const progress = order.order_details?.progress || 0;
            
            return (
              <Card key={order.id} className="p-4 md:p-6 hover:shadow-lg transition-shadow">
                <div className="flex flex-col md:flex-row md:items-start md:justify-between mb-4 space-y-3 md:space-y-0">
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-2 md:gap-3 mb-2">
                      <h3 className="text-base md:text-lg font-semibold text-slate-900">
                        {order.order_number}
                      </h3>
                      {getStatusBadge(order.status)}
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 md:gap-4 mt-3">
                      <div className="flex items-center gap-2 text-xs md:text-sm text-slate-600">
                        <User className="w-4 h-4 flex-shrink-0" />
                        <span className="truncate">{order.customer_name}</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs md:text-sm text-slate-600">
                        <Building2 className="w-4 h-4 flex-shrink-0" />
                        <span className="truncate">{business?.name || 'N/A'}</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs md:text-sm text-slate-600">
                        <Wrench className="w-4 h-4 flex-shrink-0" />
                        <span className="truncate">{order.service_type}</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs md:text-sm text-slate-600">
                        <Calendar className="w-4 h-4 flex-shrink-0" />
                        <span className="text-xs">{formatDate(order.created_at)}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-left md:text-right">
                    <div className="text-xs md:text-sm text-slate-500 mb-1">Nilai Pekerjaan</div>
                    <div className="text-lg md:text-xl font-bold text-slate-900">
                      {formatCurrency(order.total_amount)}
                    </div>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs md:text-sm font-medium text-slate-700">Progress</span>
                    <span className="text-xs md:text-sm font-bold text-slate-900">{progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 md:h-3">
                    <div 
                      className={`h-2 md:h-3 rounded-full transition-all ${getProgressColor(progress)}`}
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                </div>

                {/* Notes */}
                {order.notes && (
                  <div className="mb-4 p-3 bg-slate-50 rounded-lg">
                    <div className="text-xs font-medium text-slate-500 mb-1">Catatan:</div>
                    <div className="text-xs md:text-sm text-slate-700 whitespace-pre-line">{order.notes}</div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex flex-col sm:flex-row gap-2">
                  <Button 
                    onClick={() => {
                      setSelectedOrder(order);
                      setShowProgressModal(true);
                    }}
                    className="min-h-[44px] w-full sm:w-auto bg-blue-600 hover:bg-blue-700"
                  >
                    <TrendingUp className="w-4 h-4 mr-2" />
                    Progress Detail
                  </Button>
                  <Button 
                    onClick={() => handleUpdateStatus(order)}
                    disabled={order.status === 'completed' || order.status === 'cancelled'}
                    className="min-h-[44px] w-full sm:w-auto"
                    variant="outline"
                  >
                    <Clock className="w-4 h-4 mr-2" />
                    Update Status
                  </Button>
                  {order.customer_phone && (
                    <Button variant="outline" className="min-h-[44px] w-full sm:w-auto">
                      <span>📞 {order.customer_phone}</span>
                    </Button>
                  )}
                </div>
              </Card>
            );
          })}

          {orders.length === 0 && (
            <Card className="p-12 text-center">
              <Wrench className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Tidak Ada Pekerjaan</h3>
              <p className="text-slate-600">Belum ada pekerjaan yang di-assign ke Anda</p>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="pending" className="space-y-4 mt-6">
          {getPendingOrders().length === 0 ? (
            <Card className="p-12 text-center">
              <AlertCircle className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Tidak Ada Pending</h3>
              <p className="text-slate-600">Semua pekerjaan sudah dimulai atau selesai</p>
            </Card>
          ) : (
            getPendingOrders().map((order) => {
              const business = businesses.find(b => b.id === order.business_id);
              return (
                <Card key={order.id} className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-slate-900">{order.order_number}</h3>
                      <p className="text-sm text-slate-600">{order.customer_name} - {order.service_type}</p>
                    </div>
                    <Button onClick={() => handleUpdateStatus(order)}>
                      Mulai Pekerjaan
                    </Button>
                  </div>
                </Card>
              );
            })
          )}
        </TabsContent>

        <TabsContent value="processing" className="space-y-4 mt-6">
          {getProcessingOrders().length === 0 ? (
            <Card className="p-12 text-center">
              <PlayCircle className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Tidak Ada Yang Sedang Proses</h3>
            </Card>
          ) : (
            getProcessingOrders().map((order) => {
              const business = businesses.find(b => b.id === order.business_id);
              const progress = order.order_details?.progress || 0;
              return (
                <Card key={order.id} className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="font-semibold text-slate-900">{order.order_number}</h3>
                      <p className="text-sm text-slate-600">{order.customer_name} - {order.service_type}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-blue-600">{progress}%</div>
                      <div className="text-xs text-slate-500">Progress</div>
                    </div>
                  </div>
                  <Button onClick={() => handleUpdateStatus(order)} className="w-full">
                    Update Progress
                  </Button>
                </Card>
              );
            })
          )}
        </TabsContent>

        <TabsContent value="completed" className="space-y-4 mt-6">
          {getCompletedOrders().length === 0 ? (
            <Card className="p-12 text-center">
              <CheckCircle className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Belum Ada Yang Selesai</h3>
            </Card>
          ) : (
            getCompletedOrders().map((order) => {
              const business = businesses.find(b => b.id === order.business_id);
              return (
                <Card key={order.id} className="p-6 bg-green-50">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-slate-900">{order.order_number}</h3>
                      <p className="text-sm text-slate-600">{order.customer_name} - {order.service_type}</p>
                      {order.completion_date && (
                        <p className="text-xs text-slate-500 mt-1">
                          Selesai: {formatDate(order.completion_date)}
                        </p>
                      )}
                    </div>
                    <CheckCircle className="w-8 h-8 text-green-600" />
                  </div>
                </Card>
              );
            })
          )}
        </TabsContent>
      </Tabs>

      {/* Update Status Modal */}
      <Dialog open={showUpdateModal} onOpenChange={setShowUpdateModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Update Status Pekerjaan</DialogTitle>
          </DialogHeader>
          
          {selectedOrder && (
            <div className="space-y-4">
              <div>
                <div className="text-sm font-medium text-slate-700 mb-1">Order</div>
                <div className="text-lg font-semibold">{selectedOrder.order_number}</div>
                <div className="text-sm text-slate-600">{selectedOrder.customer_name}</div>
              </div>

              <div>
                <label className="text-sm font-medium text-slate-700 mb-2 block">
                  Status
                </label>
                <Select value={updateData.status} onValueChange={(val) => setUpdateData({...updateData, status: val})}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="processing">Dalam Proses</SelectItem>
                    <SelectItem value="completed">Selesai</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium text-slate-700 mb-2 block">
                  Progress: {updateData.progress}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="10"
                  value={updateData.progress}
                  onChange={(e) => setUpdateData({...updateData, progress: parseInt(e.target.value)})}
                  className="w-full"
                />
              </div>

              <div>
                <label className="text-sm font-medium text-slate-700 mb-2 block">
                  Catatan
                </label>
                <Textarea
                  value={updateData.notes}
                  onChange={(e) => setUpdateData({...updateData, notes: e.target.value})}
                  placeholder="Tambahkan catatan pekerjaan..."
                  rows={4}
                />
              </div>

              <div className="flex gap-2">
                <Button onClick={handleSubmitUpdate} className="flex-1">
                  Simpan Update
                </Button>
                <Button variant="outline" onClick={() => setShowUpdateModal(false)}>
                  Batal
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
