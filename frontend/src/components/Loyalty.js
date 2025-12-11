import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';
import { getUser } from '../utils/auth';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Gift, Plus, Edit, Trash2, Users, DollarSign, TrendingUp, Calendar } from 'lucide-react';
import { toast } from 'sonner';

export default function Loyalty() {
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingProgram, setEditingProgram] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    start_date: '',
    end_date: '',
    target_participants: 0,
    budget: 0,
    reward_type: '',
    status: 'planning'
  });
  
  const currentUser = getUser();
  const canEdit = currentUser && [1, 2].includes(currentUser.role_id);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await api.get('/loyalty-programs');
      setPrograms(response.data);
    } catch (error) {
      toast.error('Gagal memuat data program loyalitas');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const submitData = {
        ...formData,
        start_date: new Date(formData.start_date).toISOString(),
        end_date: new Date(formData.end_date).toISOString()
      };
      
      if (editingProgram) {
        await api.put(`/loyalty-programs/${editingProgram.id}`, {
          status: submitData.status,
          actual_participants: formData.actual_participants,
          actual_cost: formData.actual_cost
        });
        toast.success('Program berhasil diupdate!');
      } else {
        await api.post('/loyalty-programs', submitData);
        toast.success('Program berhasil ditambahkan!');
      }
      setShowForm(false);
      setEditingProgram(null);
      resetForm();
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Gagal menyimpan program');
    }
  };

  const handleEdit = (program) => {
    setEditingProgram(program);
    setFormData({
      name: program.name,
      description: program.description,
      start_date: new Date(program.start_date).toISOString().split('T')[0],
      end_date: new Date(program.end_date).toISOString().split('T')[0],
      target_participants: program.target_participants,
      budget: program.budget,
      reward_type: program.reward_type,
      status: program.status,
      actual_participants: program.actual_participants || 0,
      actual_cost: program.actual_cost || 0
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Yakin ingin menghapus program ini?')) return;
    
    try {
      await api.delete(`/loyalty-programs/${id}`);
      toast.success('Program berhasil dihapus!');
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Gagal menghapus program');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      start_date: '',
      end_date: '',
      target_participants: 0,
      budget: 0,
      reward_type: '',
      status: 'planning'
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
      month: 'long',
      day: 'numeric'
    });
  };

  const getStatusBadge = (status) => {
    const config = {
      planning: { label: 'Planning', color: 'bg-yellow-100 text-yellow-800' },
      active: { label: 'Aktif', color: 'bg-green-100 text-green-800' },
      completed: { label: 'Selesai', color: 'bg-blue-100 text-blue-800' },
      cancelled: { label: 'Dibatalkan', color: 'bg-red-100 text-red-800' }
    };
    const cfg = config[status] || config.planning;
    return <Badge className={cfg.color}>{cfg.label}</Badge>;
  };

  if (loading) {
    return <div className="flex items-center justify-center h-96">Memuat data...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 tracking-tight mb-2">Program Loyalitas</h1>
          <p className="text-slate-600">Kelola program loyalitas dan reward pelanggan</p>
        </div>
        {canEdit && (
          <Button onClick={() => setShowForm(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Tambah Program
          </Button>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="text-sm text-slate-500">Total Program</div>
          <div className="text-3xl font-bold text-slate-900 mt-1">{programs.length}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-slate-500">Aktif</div>
          <div className="text-3xl font-bold text-green-600 mt-1">
            {programs.filter(p => p.status === 'active').length}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-slate-500">Total Partisipan</div>
          <div className="text-3xl font-bold text-blue-600 mt-1">
            {programs.reduce((sum, p) => sum + (p.actual_participants || 0), 0)}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-slate-500">Total Budget</div>
          <div className="text-2xl font-bold text-slate-900 mt-1">
            {formatCurrency(programs.reduce((sum, p) => sum + p.budget, 0))}
          </div>
        </Card>
      </div>

      {/* Programs List */}
      <div className="space-y-4">
        {programs.length === 0 ? (
          <Card className="p-12 text-center">
            <Gift className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Tidak Ada Program</h3>
            <p className="text-slate-600">Belum ada program loyalitas yang dibuat</p>
          </Card>
        ) : (
          programs.map((program) => (
            <Card key={program.id} className="p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold text-slate-900">{program.name}</h3>
                    {getStatusBadge(program.status)}
                  </div>
                  <p className="text-slate-600 mb-3">{program.description}</p>
                  <div className="flex items-center gap-4 text-sm text-slate-500">
                    <div className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      <span>{formatDate(program.start_date)} - {formatDate(program.end_date)}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Gift className="w-4 h-4" />
                      <span>{program.reward_type}</span>
                    </div>
                  </div>
                </div>
                {canEdit && (
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" onClick={() => handleEdit(program)}>
                      <Edit className="w-4 h-4" />
                    </Button>
                    {currentUser.role_id === 1 && (
                      <Button size="sm" variant="outline" onClick={() => handleDelete(program.id)}>
                        <Trash2 className="w-4 h-4 text-red-600" />
                      </Button>
                    )}
                  </div>
                )}
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t">
                <div>
                  <div className="text-xs text-slate-500 mb-1">Target Partisipan</div>
                  <div className="flex items-center gap-2">
                    <Users className="w-4 h-4 text-slate-400" />
                    <span className="font-semibold text-slate-900">{program.target_participants}</span>
                  </div>
                </div>
                <div>
                  <div className="text-xs text-slate-500 mb-1">Actual Partisipan</div>
                  <div className="flex items-center gap-2">
                    <Users className="w-4 h-4 text-green-600" />
                    <span className="font-semibold text-green-600">{program.actual_participants || 0}</span>
                  </div>
                </div>
                <div>
                  <div className="text-xs text-slate-500 mb-1">Budget</div>
                  <div className="flex items-center gap-2">
                    <DollarSign className="w-4 h-4 text-slate-400" />
                    <span className="font-semibold text-slate-900">{formatCurrency(program.budget)}</span>
                  </div>
                </div>
                <div>
                  <div className="text-xs text-slate-500 mb-1">Actual Cost</div>
                  <div className="flex items-center gap-2">
                    <DollarSign className="w-4 h-4 text-blue-600" />
                    <span className="font-semibold text-blue-600">{formatCurrency(program.actual_cost || 0)}</span>
                  </div>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="mt-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-slate-700">Progress</span>
                  <span className="text-sm font-bold text-slate-900">
                    {Math.round((program.actual_participants || 0) / program.target_participants * 100)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full transition-all"
                    style={{ width: `${Math.min(100, (program.actual_participants || 0) / program.target_participants * 100)}%` }}
                  ></div>
                </div>
              </div>
            </Card>
          ))
        )}
      </div>

      {/* Form Dialog */}
      <Dialog open={showForm} onOpenChange={setShowForm}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{editingProgram ? 'Edit Program Loyalitas' : 'Tambah Program Loyalitas'}</DialogTitle>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label>Nama Program *</Label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                required
                placeholder="Contoh: Promo Akhir Tahun 2024"
              />
            </div>

            <div>
              <Label>Deskripsi *</Label>
              <Textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                required
                rows={3}
                placeholder="Detail program loyalitas..."
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Tanggal Mulai *</Label>
                <Input
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({...formData, start_date: e.target.value})}
                  required
                />
              </div>
              <div>
                <Label>Tanggal Selesai *</Label>
                <Input
                  type="date"
                  value={formData.end_date}
                  onChange={(e) => setFormData({...formData, end_date: e.target.value})}
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Target Partisipan *</Label>
                <Input
                  type="number"
                  value={formData.target_participants}
                  onChange={(e) => setFormData({...formData, target_participants: parseInt(e.target.value)})}
                  required
                  min="0"
                />
              </div>
              <div>
                <Label>Budget (Rp) *</Label>
                <Input
                  type="number"
                  value={formData.budget}
                  onChange={(e) => setFormData({...formData, budget: parseFloat(e.target.value)})}
                  required
                  min="0"
                  step="1000"
                />
              </div>
            </div>

            <div>
              <Label>Jenis Reward *</Label>
              <Input
                value={formData.reward_type}
                onChange={(e) => setFormData({...formData, reward_type: e.target.value})}
                required
                placeholder="Contoh: Voucher, Points, Discount, Cashback"
              />
            </div>

            <div>
              <Label>Status *</Label>
              <Select 
                value={formData.status} 
                onValueChange={(val) => setFormData({...formData, status: val})}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="planning">Planning</SelectItem>
                  <SelectItem value="active">Aktif</SelectItem>
                  <SelectItem value="completed">Selesai</SelectItem>
                  <SelectItem value="cancelled">Dibatalkan</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {editingProgram && (
              <div className="grid grid-cols-2 gap-4 p-4 bg-blue-50 rounded-lg">
                <div>
                  <Label>Actual Partisipan</Label>
                  <Input
                    type="number"
                    value={formData.actual_participants || 0}
                    onChange={(e) => setFormData({...formData, actual_participants: parseInt(e.target.value)})}
                    min="0"
                  />
                </div>
                <div>
                  <Label>Actual Cost (Rp)</Label>
                  <Input
                    type="number"
                    value={formData.actual_cost || 0}
                    onChange={(e) => setFormData({...formData, actual_cost: parseFloat(e.target.value)})}
                    min="0"
                    step="1000"
                  />
                </div>
              </div>
            )}

            <div className="flex gap-2 pt-4">
              <Button type="submit" className="flex-1">
                {editingProgram ? 'Update' : 'Simpan'}
              </Button>
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => {
                  setShowForm(false);
                  setEditingProgram(null);
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